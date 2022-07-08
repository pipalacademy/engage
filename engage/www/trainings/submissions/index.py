import frappe

from engage.utils import format_datetime_diff, require_login, require_trainer_role, with_training


@require_login
@with_training
@require_trainer_role
def get_context(context, training):
    pagination_params = get_pagination_parameters_from_form_dict(
        frappe.form_dict)

    context.training = training
    context.submissions = frappe.get_all(
        "Practice Problem Latest Submission",
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
            "code",
        ],
        filters={"training": training.name},
        order_by="submitted_at desc, modified desc",
        **pagination_params)

    context.format_datetime_diff = format_datetime_diff
    context.get_submission_url = get_submission_url


def get_submission_url(submission):
    return f"/trainings/{submission.training}/submissions/{submission.problem_set}/{submission.problem}?participant={submission.author}"


def get_pagination_parameters_from_form_dict(d):
    page_length = 60
    page = int(d.page) if "page" in d else 1

    start = (page - 1) * page_length

    return dict(page_length=page_length, start=start)
