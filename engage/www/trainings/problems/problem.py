import frappe

from engage.utils import require_login, with_problem, with_training


@require_login
@with_training
@with_problem
def get_context(context, training, problem):
    pset_name = frappe.form_dict.problem_set
    psets = {pset.slug: pset for pset in training.problem_sets}
    pset_ref = psets[pset_name]

    submission_doctype = "Practice Problem Latest Submission"
    if frappe.db.exists(submission_doctype, {
            "problem": problem.name,
            "author": frappe.session.user
    }):
        solution = frappe.get_doc(submission_doctype, {
            "problem": problem.name,
            "author": frappe.session.user
        })
    else:
        solution = None

    context.t = training
    context.problem_set = pset_ref
    context.problem_set_title = pset_ref.title
    context.can_submit = pset_ref.status != "Closed"
    context.problem = problem
    context.psets = psets
    context.d = frappe.form_dict
    context.latest_submission = solution
    context.data = {
        "problem_set": pset_ref.problem_set,
        "problem": problem.name,
        "runtime": problem.runtime,
        "training": training.name,
        "submission_json": solution and solution.test_result or "null"
    }

    context.title = problem.title
