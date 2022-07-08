import frappe

from engage.utils import format_datetime_diff, require_login, require_trainer_role, with_training


@require_login
@with_training
@require_trainer_role
def get_context(context, training):
    context.training = training
    context.submissions = frappe.get_all(
        "Practice Problem Latest Submission",
        fields=[
            "name",
            "author",
            "author_full_name",
            "problem_set_title",
            "problem",
            "problem_title",
            "submitted_at",
            "modified",
            "test_outcome",
            "comment_count",
            "code",
        ],
        order_by="submitted_at desc, modified desc")
    context.format_datetime_diff = format_datetime_diff
