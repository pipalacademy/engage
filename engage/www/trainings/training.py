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

    participants = frappe.get_all("Training Participant", filters={"parent": tname}, fields=["jh_username", "jh_password", "parent", "user"])

    solved_by_user = {}
    for p in participants:
        solved_by_user[p["user"]] = {}

    rows = frappe.get_all(
        "Practice Problem Latest Submission", 
        filters={"training": tname}, 
        fields=["author", "problem"], 
        page_length=1000)

    for row in rows:
        solved_by_user[row["author"]][row["problem"]] = row

    count_solved_by_user = [{
            "count": len(submissions),
            "full_name": frappe.get_cached_doc("User", user).full_name,
            "active": user == frappe.session.user
        }
        for user, submissions in solved_by_user.items()
    ]

    count_solved_by_user.sort(key=lambda k: k["count"], reverse=True)

    try:
        user_participant = next(p for p in participants if p.user == frappe.session.user)
    except StopIteration:
        user_participant = None

    nowtime = frappe.utils.now_datetime()
    modified = False

    for pset in training.problem_sets:
        if pset.publish_time and pset.status == "Pending" and nowtime >= pset.publish_time:
            pset.status = "Published"
            modified = True

        if pset.deadline and pset.status in {"Published", "Pending"} and nowtime >= pset.deadline:
            pset.status = "Closed"
            modified = True

    if modified:
        training.save(ignore_permissions=True)
        frappe.db.commit()

    context.t = training
    context.client = client
    context.participant = user_participant

    context.title = training.title
    context.submissions = solved_by_user.get(frappe.session.user, {})
    context.count_solved_by_user = count_solved_by_user

def get_training(id):
    try:
        return frappe.get_doc("Training", id)
    except frappe.exceptions.DoesNotExistError:
        return


def time_is_between(val, lesser, greater):
    return lesser <= val and val <= greater
