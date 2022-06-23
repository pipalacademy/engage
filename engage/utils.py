from functools import wraps
from urllib.parse import urlencode

import frappe
from frappe import request


NotFoundTemplate = "www/404.html"


def require_login(fn):
    @wraps(fn)
    def redirect_if_guest(context, *args, **kwargs):
        if frappe.session.user == "Guest":
            frappe.local.flags.redirect_location = "/login?" + urlencode({"redirect-to": request.full_path})
            raise frappe.Redirect

        return fn(context, *args, **kwargs)

    return redirect_if_guest


def with_training(fn):
    @wraps(fn)
    def fetch_training_or_404(context, *args, **kwargs):
        try:
            year = frappe.form_dict["year"]
            slug = frappe.form_dict["slug"]
        except KeyError:
            context.template = NotFoundTemplate
            return
        else:
            training_name = f"{year}/{slug}"

        training = get_training(training_name)
        if not training:
            context.template = NotFoundTemplate
            return

        return fn(context, *args, **kwargs, training=training)

    return fetch_training_or_404


def require_trainer_role(fn):
    @wraps(fn)
    def check_role(context, *args, training, **kwargs):
        if not training.has_user_as_trainer(frappe.session.user):
            context.template = NotFoundTemplate
            return

        return fn(context, *args, training, **kwargs)

    return check_role


def get_training(name):
    try:
        return frappe.get_doc("Training", name)
    except frappe.exceptions.DoesNotExistError:
        return

