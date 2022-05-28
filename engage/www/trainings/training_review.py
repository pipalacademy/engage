import frappe


NOT_FOUND_TEMPLATE = "www/404.html"


def get_context(context):
    try:
        year = frappe.form_dict["year"]
        slug = frappe.form_dict["slug"]
    except KeyError:
        context.template = NOT_FOUND_TEMPLATE
        return

    t = get_training(year, slug)
    if not t:
        context.template = NOT_FOUND_TEMPLATE
        return

    if not t.has_user_as_trainer(frappe.session.user):
        context.template = NOT_FOUND_TEMPLATE
        return

    participants = t.participants
    for p in participants:
        p.full_name = frappe.get_cached_doc("User", p.user).full_name

    trainers = t.trainers
    for trainer in trainers:
        trainer.full_name = frappe.get_cached_doc("User", trainer.user).full_name

    problem_sets = [frappe.get_cached_doc("Problem Set", row.problem_set) for row in t.problem_sets]
    for ps in problem_sets:
        ps.problems = [frappe.get_doc("Practice Problem", p.problem) for p in ps.problems]

        for p in ps.problems:
            p.code = p.code_files[0].content

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
