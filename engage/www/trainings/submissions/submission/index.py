# import frappe

from engage.utils import format_datetime_diff, require_login, require_trainer_role, with_submission, with_training


@require_login
@with_training
@with_submission
@require_trainer_role
def get_context(context, training, submission):
    context.training = training
    context.submission = submission
    context.format_datetime_diff = format_datetime_diff
