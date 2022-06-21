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

    context.t = training
    context.title = training.title

    context.participant = member = get_member(training, frappe.session.user)
    if member and member.is_trainer:
        training.can_review = True

    if not member:
        return

    user_submissions_list = frappe.get_all(
        "Practice Problem Latest Submission",
        filters={
            "training": tname,
            "author": member.user
        },
        fields=["problem"],
        page_length=1000)
    user_submissions = {sub["problem"]: sub for sub in user_submissions_list}

    if training.refresh_problem_sets():
        training.save(ignore_permissions=True)
        frappe.db.commit()

    problem_sets = [
        pset for pset in training.problem_sets if pset.is_published
    ]

    context.problem_sets = problem_sets
    context.submissions = user_submissions


def get_training(id):
    try:
        return frappe.get_doc("Training", id)
    except frappe.exceptions.DoesNotExistError:
        return


def time_is_between(val, lesser, greater):
    return lesser <= val and val <= greater


def get_member(training, username):
    for p in training.participants:
        if p.user == username:
            p.is_trainer = training.has_user_as_trainer(p.user)
            return p

    for t in training.trainers:
        if t.user == username:
            t.is_trainer = True
            t.jh_username = getattr(t, "jh_username", None)
            t.jh_password = getattr(t, "jh_password", None)
            return t

    return
