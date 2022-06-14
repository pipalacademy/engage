import frappe


NOT_FOUND_TEMPLATE = "www/404.html"


def get_context(context):
    try:
        year = frappe.form_dict["year"]
        slug = frappe.form_dict["slug"]
    except KeyError:
        context.template = NOT_FOUND_TEMPLATE
        return

    username = frappe.form_dict.get("p")

    t = get_training(year, slug)
    if not t or not t.has_user_as_trainer(frappe.session.user):
        context.template = NOT_FOUND_TEMPLATE
        return

    participants = t.participants
    for p in participants:
        p.full_name = frappe.get_cached_doc("User", p.user).full_name

    trainers = t.trainers
    for trainer in trainers:
        trainer.full_name = frappe.get_cached_doc("User", trainer.user).full_name

    problem_sets = [frappe.get_cached_doc("Problem Set", row.problem_set) for row in t.problem_sets]

    for pset in problem_sets:
        pset.problems = [frappe.get_doc("Practice Problem", p.problem) for p in pset.problems]

        for problem in pset.problems:
            latest_submission = username and get_latest_submission(username, t.name, pset.name, problem.name)
            problem.code = latest_submission and latest_submission.code or problem.code_files[0].content

    context.t = t
    context.title = t.title
    context.client = frappe.get_doc("Client", t.client)
    context.participants = participants
    context.trainers = trainers
    context.num_participants = len(participants)
    context.problem_sets = problem_sets


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


def get_latest_submission(author, training, problem_set, problem):
    doc_list = frappe.get_list("Practice Problem Latest Submission",
            filters={"author": author, "training": training, "problem_set": problem_set, "problem": problem},
            fields="*",
            page_length=1)

    latest = doc_list and doc_list[0] or None
    return latest
