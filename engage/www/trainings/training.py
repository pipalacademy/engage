import frappe


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

    participants = frappe.get_all("Training Participant", filters={"user": frappe.session.user, "parent": tname}, fields=["jh_username", "jh_password", "parent"])

    rows = frappe.get_all(
        "Practice Problem Submission", 
        filters={"training": tname, "author": frappe.session.user}, 
        fields="*", 
        page_length=1000)
    
    submissions = {row.problem: row for row in rows}

    context.t = training
    context.client = client
    context.participant = participants and participants[0] or None

    context.title = t.title
    context.submissions = submissions


def get_training(id):
    try:
        return frappe.get_doc("Training", id)
    except frappe.exceptions.DoesNotExistError:
        return
