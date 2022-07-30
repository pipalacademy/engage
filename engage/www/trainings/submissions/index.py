from math import ceil
from urllib.parse import urlencode

import frappe
from frappe.utils import get_fullname

from engage.utils import format_datetime_diff, get_submissions, require_login, require_trainer_role, with_training

PAGE_LENGTH = 60


@require_login
@with_training
@require_trainer_role
def get_context(context, training):
    context.training = training

    pset_names = [pset.problem_set for pset in training.problem_sets]
    context.problems = frappe.get_all("Problem Reference",
                                      fields=["problem", "problem_title"],
                                      filters={
                                          "parenttype": "Problem Set",
                                          "parent": ["IN", pset_names]
                                      })

    author_usernames = [p.user for p in training.participants] + [p.user for p in training.trainers]
    context.possible_authors = [{
        "username": username,
        "full_name": get_fullname(username)
    } for username in author_usernames]

    context.zip = zip


def get_submissions_url(training_name, **querydict):
    return f"/trainings/{training_name}/submissions?" + urlencode(querydict)


def get_submission_url(submission):
    return f"/trainings/{submission.training}/submissions/{submission.name}"


def get_pagination_parameters_from_form_dict(d):
    page = get_current_page(frappe.form_dict)
    start = (page - 1) * PAGE_LENGTH

    return dict(page_length=PAGE_LENGTH, start=start)


def get_current_page(d):
    return int(d.page) if "page" in d else 1
