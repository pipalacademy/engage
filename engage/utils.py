import cProfile
import pstats
from functools import wraps
from pstats import SortKey
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
        submission_name = frappe.form_dict.get("submission")
        if not submission_name:
            context.template = NotFoundTemplate
            return

        submission = get_submission(submission_name)
        if not submission or submission.training != training.name:
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

        return fn(context, *args, training=training, **kwargs)

    return check_role


def with_profiler(fn):

    @wraps(fn)
    def wrapper(context, *args, **kwargs):
        with cProfile.Profile() as pr:
            return_value = fn(context, *args, **kwargs)

        ps = pstats.Stats(pr)
        ps.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(20)

        return return_value

    return wrapper


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


def get_submission(submission_name):
    try:
        return frappe.get_doc("Practice Problem Latest Submission",
                              submission_name)
    except frappe.exceptions.DoesNotExistError:
        return


def format_datetime_diff(diff,
                         years_suffix="y",
                         months_suffix="mo",
                         days_suffix="d",
                         hours_suffix="h",
                         minutes_suffix="m",
                         seconds_suffix="s"):
    """
    argument diff must be of type `datetime.timedelta`
    """

    years = diff.days // 360
    months = (diff.days - years * 360) // 30
    days = diff.days % 30

    hours = diff.seconds // 3600
    minutes = (diff.seconds - hours * 3600) // 60
    seconds = diff.seconds % 60

    significance_order = [(years, years_suffix), (months, months_suffix),
                          (days, days_suffix), (hours, hours_suffix),
                          (minutes, minutes_suffix), (seconds, seconds_suffix)]

    most_significant_duration = next((str(count), unit)
                                     for (count, unit) in significance_order
                                     if count or unit == "s")

    return "".join(most_significant_duration)


def get_submissions(training_name,
                    fields=("name", ),
                    order_by="submitted_at desc, modified desc",
                    **kwargs):
    doctype = "Practice Problem Latest Submission"

    filters = {"training": training_name}
    if "filters" in kwargs:
        filters.update(kwargs["filters"])
        kwargs.pop("filters")

    return frappe.get_all(doctype,
                          filters=filters,
                          fields=fields,
                          order_by=order_by,
                          **kwargs)


def get_submissions_with_listing_fields(training_name, **kwargs):
    fields = [
        "name",
        "author",
        "author_full_name",
        "problem_set",
        "problem_set_title",
        "problem",
        "problem_title",
        "training",
        "submitted_at",
        "modified",
        "test_outcome",
        "comment_count",
        "for_review",
        "code",
    ]
    return get_submissions(training_name, fields=fields, **kwargs)


def get_submissions_count(training_name, **kwargs):
    fields = ["count(name) as count"]
    result = get_submissions(training_name, fields=fields, **kwargs)
    return result[0]["count"]


def get_next_submission(submission):
    subs_list = get_submissions(
        submission.training,
        filters={"submitted_at": ["<", submission.submitted_at]},
        order_by="submitted_at desc, modified desc",
        page_length=1)

    return subs_list and subs_list[0] or None


def get_prev_submission(submission):
    subs_list = get_submissions(
        submission.training,
        filters={"submitted_at": [">", submission.submitted_at]},
        order_by="submitted_at asc, modified asc",
        page_length=1)

    return subs_list and subs_list[0] or None


def get_submission_url(training_name, submission_name):
    return f"/trainings/{training_name}/submissions/{submission_name}"
