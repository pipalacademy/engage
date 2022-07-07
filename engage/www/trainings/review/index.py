import frappe

from engage.utils import require_login, require_trainer_role, with_training


@require_login
@with_training
@require_trainer_role
def get_context(context, training):
    context.training = training
    context.submissions = frappe.get_all("Practice Problem Latest Submission",
                                         fields=[
                                             "name",
                                             "author",
                                             "author_full_name",
                                             "problem_set_title",
                                             "problem",
                                             "problem_title",
                                             "submitted_at",
                                             "code",
                                         ],
                                         filters={"for_review": True})
    context.format_datetime_diff = format_datetime_diff


def format_datetime_diff(dt1, dt2):
    diff = dt1 - dt2

    years = diff.days // 360
    months = (diff.days - years * 360) // 30
    days = diff.days % 30

    hours = diff.seconds // 3600
    minutes = (diff.seconds - hours * 3600) // 60
    seconds = diff.seconds % 60

    significance_order = [(years, "y"), (months, "mo"), (days, "d"),
                          (hours, "h"), (minutes, "m"), (seconds, "s")]

    most_significant_duration = next((str(count), unit)
                                     for (count, unit) in significance_order
                                     if count or unit == "s")

    return "".join(most_significant_duration)
