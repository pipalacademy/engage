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

    training = get_training(year, slug)
    if not (training and training.has_user_as_trainer(frappe.session.user)):
        context.template = NOT_FOUND_TEMPLATE
        return

    if training.refresh_problem_sets():
        training.save(ignore_permissions=True)
        frappe.db.commit()

    published_problem_sets = [
        frappe.get_doc("Problem Set", ps.problem_set)
        for ps in training.problem_sets if ps.is_published
    ]

    participant_name = frappe.form_dict.get("participant")
    participant = get_participant_from(training.participants, participant_name)

    problem_name = frappe.form_dict.get("problem")
    problem = get_problem(published_problem_sets, problem_name)

    submissions = get_latest_submissions_for_training(training.name)

    for p in training.participants:
        p.full_name = frappe.get_cached_doc("User", p.user).full_name
        p.active = p.name == participant.name
        p.num_solved = len(submissions.get(p.user, []))

    context.training = training
    context.q = remove_none({
        "participant": participant_name,
        "problem": problem_name
    })
    context.dictupdate = dictupdate
    context.problem_sets = published_problem_sets
    context.problem = problem
    context.participant = participant
    context.user_submissions = submissions.get(participant.user, {})
    context.submission = submissions.get(participant.user,
                                         {}).get(problem.name)
    # context.client = frappe.get_doc("Client", training.client)
    # context.q = {"participant": participant_name, "problem": problem_name}


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

    try:
        return next(item for item in itr if key(item))
    except StopIteration:
        None


def get_participant_from(participants, participant_name):
    if participant_name:
        participant = get_first_truthy(
            participants, key=lambda p: p.user == participant_name)
    else:
        participant = get_first_truthy(participants)

    return participant


def get_problem(problem_sets, problem_name):
    if problem_name:
        problem = frappe.get_doc("Practice Problem", problem_name)
    else:
        first_pset = get_first_truthy(problem_sets, key=lambda ps: ps.problems)
        problem_name = first_pset and first_pset.problems[0].problem
        problem = problem_name and frappe.get_doc("Practice Problem",
                                                  problem_name)

    return problem


def remove_none(dict_):
    return {k: v for k, v in dict_.items() if v is not None}


def dictupdate(dict_, updates):
    ret = dict_.copy()
    ret.update(updates)
    return ret
