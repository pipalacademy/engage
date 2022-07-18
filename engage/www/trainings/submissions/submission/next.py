import frappe

from engage.utils import NotFoundTemplate, get_next_submission, get_submission_url, require_login, require_trainer_role, with_submission, with_training


@require_login
@with_training
@require_trainer_role
@with_submission
def get_context(context, *, training, submission):
    next_submission = get_next_submission(submission)
    if not next_submission:
        context.template = NotFoundTemplate
        return

    url = get_submission_url(training.name, next_submission["name"])

    frappe.local.flags.redirect_location = url
    raise frappe.Redirect
