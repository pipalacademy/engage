from math import ceil
from urllib.parse import urlencode

import frappe

from engage.utils import format_datetime_diff, get_submissions, require_login, require_trainer_role, with_training

PAGE_LENGTH = 60


@require_login
@with_training
@require_trainer_role
def get_context(context, training):
    context.training = training

    pagination_params = get_pagination_parameters_from_form_dict(
        frappe.form_dict)

    context.submissions = get_submissions(training.name,
                                          fields=[
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
                                          ],
                                          **pagination_params)

    submissions_doctype = "Practice Problem Latest Submission"
    total_submissions = frappe.db.count(submissions_doctype,
                                        filters={"training": training.name})
    context.total_pages = ceil(total_submissions / PAGE_LENGTH)
    context.current_page = get_current_page(frappe.form_dict)

    context.format_datetime_diff = format_datetime_diff
    context.get_submissions_url = get_submissions_url
    context.get_submission_url = get_submission_url


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
