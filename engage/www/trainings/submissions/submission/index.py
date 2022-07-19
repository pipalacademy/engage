import frappe

from engage.utils import get_prev_submission, get_next_submission, get_submission_url, format_datetime_diff, require_login, require_trainer_role, with_submission, with_training


@require_login
@with_training
@with_submission
@require_trainer_role
def get_context(context, training, submission):
    context.training = training
    context.submission = submission
    context.problem = get_problem(submission.problem)
    context.format_datetime_diff = format_datetime_diff

    context.has_prev = get_prev_submission(submission) is not None
    context.has_next = get_next_submission(submission) is not None

    this_url = get_submission_url(submission.training, submission.name)
    context.prev_submission_url = this_url + "/prev"
    context.next_submission_url = this_url + "/next"


def get_problem(problem_name):
    return frappe.get_doc("Practice Problem", problem_name)
