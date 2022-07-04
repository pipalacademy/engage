from pathlib import Path

import frappe

from engage.utils import require_login, with_problem, with_training


@require_login
@with_training
@with_problem
def get_context(context, training, problem):
    context.training = training
    context.problem = problem

    problem_set_name = frappe.form_dict.problem_set
    problem_set = next(pset for pset in training.problem_sets
                       if pset.slug == problem_set_name)
    context.problem_set = problem_set

    problem.url = get_problem_url(training, problem_set, problem)

    context.submission = get_submission(problem.name, frappe.session.user)


def get_problem_url(training, pset_ref, problem):
    return f"/trainings/{training.name}/problems/{pset_ref.slug}/{problem.name}"


def truncate_filepath(filepath):
    path = Path(filepath)

    parents = path.parent.parts
    filename = path.name

    truncated_parts = [*(part[0] for part in parents), filename]

    return "/".join(truncated_parts)


def get_submission(problem_name, user_name):
    doctype = "Practice Problem Latest Submission"
    filters = {"problem": problem_name, "author": user_name}

    if frappe.db.exists(doctype, filters):
        return frappe.get_last_doc(doctype, filters=filters)

    return
