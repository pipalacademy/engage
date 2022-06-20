import frappe

from engage.utils import require_login


@require_login
def get_context(context):
    context.no_cache = 1

    try:
        year = frappe.form_dict["year"]
        slug = frappe.form_dict["slug"]
    except KeyError:
        context.template = "www/404.html"
        return
    else:
        tname = f"{year}/{slug}"

    training = get_training(tname)
    if not training:
        context.template = "www/404.html"
        return

    if training.has_user_as_trainer(frappe.session.user):
        training.can_review = True

    client = frappe.get_doc("Client", training.client)

    participants = frappe.get_all(
        "Training Participant",
        filters={"parent": tname},
        fields=["jh_username", "jh_password", "parent", "user"])

    solved_by_user = {}
    for p in participants:
        solved_by_user[p["user"]] = {}

    rows = frappe.get_all("Practice Problem Latest Submission",
                          filters={"training": tname},
                          fields=["author", "problem"],
                          page_length=1000)

    for row in rows:
        solved_by_user[row["author"]][row["problem"]] = row

    try:
        user_participant = next(p for p in participants
                                if p.user == frappe.session.user)
    except StopIteration:
        user_participant = None

    if training.refresh_problem_sets():
        training.save(ignore_permissions=True)
        frappe.db.commit()

    problem_sets = [
        pset for pset in training.problem_sets
        if pset.status in {"Published", "Closed"}
    ]

    context.t = training
    context.client = client
    context.participant = user_participant
    context.problem_sets = problem_sets

    context.title = training.title
    context.submissions = solved_by_user.get(frappe.session.user, {})


def get_training(id):
    try:
        return frappe.get_doc("Training", id)
    except frappe.exceptions.DoesNotExistError:
        return


def time_is_between(val, lesser, greater):
    return lesser <= val and val <= greater
