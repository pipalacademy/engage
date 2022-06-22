from urllib.parse import urlencode

import frappe

from engage.utils import require_login

NOT_FOUND_TEMPLATE = "www/404.html"


@require_login
def get_context(context):
    try:
        year = frappe.form_dict["year"]
        slug = frappe.form_dict["slug"]
    except KeyError:
        context.template = NOT_FOUND_TEMPLATE
        return

    context.training = training = get_training(year, slug)
    if not (training and training.has_user_as_trainer(frappe.session.user)):
        context.template = NOT_FOUND_TEMPLATE
        return

    if training.refresh_problem_sets():
        training.save(ignore_permissions=True)
        frappe.db.commit()

    context.problem_sets = published_problem_sets = [
        frappe.get_doc("Problem Set", ps.problem_set)
        for ps in training.problem_sets if ps.is_published
    ]

    submissions = get_latest_submissions_for_training(training.name)
    for p in training.participants:
        p.num_solved = len(submissions.get(p.user, []))

    training.participants.sort(key=lambda p: p.num_solved, reverse=True)

    participant_name = frappe.form_dict.get("participant")
    participant, prev_participant, next_participant = get_participant_and_prevnext(
        training.participants, participant_name)
    context.participant, context.prev_participant, context.next_participant = participant, prev_participant, next_participant

    problem_name = frappe.form_dict.get("problem")
    problem, prev_problem, next_problem = get_problem_and_prevnext(
        published_problem_sets, problem_name)
    context.problem, context.prev_problem, context.next_problem = problem, prev_problem, next_problem

    if not problem or not participant:
        return

    for p in training.participants:
        p.full_name = frappe.get_cached_doc("User", p.user).full_name
        p.active = p.name == participant.name

    context.q = {"participant": participant_name, "problem": problem_name}
    context.get_review_link = get_review_link
    context.user_submissions = submissions.get(participant.user, {})
    context.submission = submissions.get(participant.user,
                                         {}).get(problem.name)


def get_training(year, slug):
    tname = f"{year}/{slug}"
    try:
        return frappe.get_doc("Training", tname)
    except frappe.exceptions.DoesNotExistError:
        return


def get_children(child_doctype, parent_name, parent_doctype=None, fields="*"):
    filters = {"parent": parent_name}
    if parent_doctype:
        filters.update({"parenttype": parent_doctype})

    return frappe.get_all(child_doctype, filters=filters, fields=fields)


def get_latest_submission(author, problem, **kwargs):
    doc_list = frappe.get_list(
        "Practice Problem Latest Submission",
        filters={
            "author": author,
            "problem": problem,
            **kwargs
        },
        fields="*",
        page_length=1,
    )

    latest = doc_list and doc_list[0] or None
    return latest


def get_latest_submissions_for_training(training_name):
    subs_list = frappe.get_list("Practice Problem Latest Submission",
                                filters={"training": training_name},
                                fields=["name", "author", "problem", "code"])

    subs = {}
    for sub in subs_list:
        subs.setdefault(sub["author"], {})
        subs[sub["author"]][sub["problem"]] = sub

    return subs


def get_starter_code(problem):
    return problem.code_files[0].content


def truncate(text, limit):
    if len(text) > limit:
        return text[:limit - 3] + "..."
    return text


def get_first_truthy(itr, key=None):
    key = key or (lambda x: x)

    return next_or_none(item for item in itr if key(item))


def get_participant_and_prevnext(participants, participant_name):
    prev = None

    participants_iter = iter(participants)
    for participant in participants_iter:
        if participant.user == participant_name:
            return participant, prev, next_or_none(participants_iter)
        prev = participant
    else:
        iterator = iter(participants)
        return next_or_none(iterator), None, next_or_none(iterator)


def get_problem_and_prevnext(problem_sets, problem_name):
    prev = None

    probs_iter = flatten_to_problems(problem_sets)
    for problem_ref in probs_iter:
        if problem_ref.problem == problem_name:
            problem = frappe.get_doc("Practice Problem", problem_name)
            return problem, prev, next_or_none(probs_iter)
        prev = problem_ref
    else:
        iterator = flatten_to_problems(problem_sets)
        problem_ref = next_or_none(iterator)
        problem = problem_ref and frappe.get_doc("Practice Problem",
                                                 problem_ref.problem)
        return problem, None, next_or_none(iterator)


def get_review_link(training_name, problem=None, participant=None):
    qs = {}

    if problem:
        qs.update(problem=problem)

    if participant:
        qs.update(participant=participant)

    to_append = f"?{urlencode(qs)}" if qs else ""

    return f"/trainings/{training_name}/review{to_append}"


def flatten_to_problems(problem_sets):
    for pset in problem_sets:
        yield from pset.problems


def next_or_none(iterator):
    try:
        return next(iterator)
    except StopIteration:
        return
