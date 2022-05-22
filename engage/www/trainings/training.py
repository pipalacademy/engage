import frappe


def get_context(context):
    context.no_cache = 1

    try:
        year = frappe.form_dict["year"]
        training_slug = frappe.form_dict["training_slug"]
        training_id = f"{year}/{training_slug}"
    except KeyError:
        context.template = "www/404.html"
        return

    training = get_training(training_id)
    if not training:
        context.template = "www/404.html"
        return

    context.training = training


def get_training(id):
    try:
        return frappe.get_doc("Training", id)
    except frappe.exceptions.DoesNotExistError:
        return
