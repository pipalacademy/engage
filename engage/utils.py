from functools import wraps
from urllib.parse import urlencode

import frappe
from frappe import request


def require_login(fn):
    @wraps(fn)
    def redirect_if_guest(context):
        if frappe.session.user == "Guest":
            frappe.local.flags.redirect_location = "/login?" + urlencode({"redirect-to": request.full_path})
            raise frappe.Redirect

        return fn(context)

    return redirect_if_guest
