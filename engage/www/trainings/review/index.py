import frappe

from engage.utils import require_login, require_trainer_role, with_training


@require_login
@with_training
@require_trainer_role
def get_context(context, training):
    context.training = training
    context.submissions = frappe.get_all("Practice Problem Latest Submission",
                                         fields=[
                                             "name", "author",
                                             "author_full_name",
                                             "problem_set_title", "problem",
                                             "problem_title", "code"
                                         ],
                                         filters={"for_review": True})
