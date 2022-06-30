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
