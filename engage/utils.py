from functools import wraps
from urllib.parse import urlencode

import frappe
from frappe import request

NotFoundTemplate = "www/404.html"


def require_login(fn):

    @wraps(fn)
    def redirect_if_guest(context, *args, **kwargs):
        if frappe.session.user == "Guest":
            frappe.local.flags.redirect_location = "/login?" + urlencode(
                {"redirect-to": request.full_path})
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


def with_problem(fn):

    @wraps(fn)
    def fetch_problem_or_404(context, *args, **kwargs):
        problem_name = get_problem_name_from_form_dict(frappe.form_dict)
        if not problem_name:
            context.template = NotFoundTemplate
            return

        problem = get_problem(problem_name)
        if not problem:
            context.template = NotFoundTemplate
            return

        return fn(context, *args, **kwargs, problem=problem)

    return fetch_problem_or_404


def with_submission(fn):
    """
    Requires: `with_training` decorator
    """

    @wraps(fn)
    def fetch_submission_or_404(context, *args, training, **kwargs):
        problem_set_name = get_problem_set_name_from_form_dict(
            frappe.form_dict)
        problem_name = get_problem_name_from_form_dict(frappe.form_dict)
        participant_name = get_participant_name_from_form_dict(
            frappe.form_dict)

        if not problem_set_name or not problem_name or not participant_name:
            context.template = NotFoundTemplate
            return

        submission = get_submission(training_name=training.name,
                                    problem_set_name=problem_set_name,
                                    problem_name=problem_name,
                                    author_name=participant_name)
        if not submission:
            context.template = NotFoundTemplate
            return

        return fn(context,
                  *args,
                  training=training,
                  **kwargs,
                  submission=submission)

    return fetch_submission_or_404


def require_trainer_role(fn):
    """
    Requires: `with_training` decorator
    """

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


def get_problem(name):
    try:
        return frappe.get_doc("Practice Problem", name)
    except frappe.exceptions.DoesNotExistError:
        return


def get_problem_name_from_form_dict(d):
    if "problem" not in d:
        return

    problem_name = d.problem
    if "problem_repository" in d:
        problem_name = f"{d.problem_repository}/{problem_name}"

    return problem_name


def get_problem_set_name_from_form_dict(d):
    if "problem_set" not in d:
        return

    return d.problem_set


def get_participant_name_from_form_dict(d):
    if "participant" not in d:
        return

    return d.participant


def get_submission(training_name, problem_set_name, problem_name, author_name):
    try:
        return frappe.get_last_doc("Practice Problem Latest Submission",
                                   filters={
                                       "training": training_name,
                                       "problem_set": problem_set_name,
                                       "problem": problem_name,
                                       "author": author_name
                                   })
    except frappe.exceptions.DoesNotExistError:
        return
