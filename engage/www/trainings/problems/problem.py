import frappe

from engage.utils import require_login


@require_login
def get_context(context):
    training_name = f"{frappe.form_dict.year}/{frappe.form_dict.training}"
    pset_name = frappe.form_dict.problem_set
    problem_name = frappe.form_dict.problem

    if "problem_repository" in frappe.form_dict:
        problem_name = f"{frappe.form_dict.problem_repository}/{problem_name}"

    t = frappe.get_doc("Training", training_name)
    psets = {pset.slug: pset for pset in t.problem_sets}

    problem_set_title = psets[pset_name].title

    problem = frappe.get_doc("Practice Problem", problem_name)
    doctype = "Practice Problem Latest Submission"

    if frappe.db.exists(doctype, {"problem": problem_name, "author": frappe.session.user}):
        solution = frappe.get_doc(doctype, {"problem": problem_name, "author": frappe.session.user})
    else:
        solution = None

    context.t = t
    context.problem_set = psets[pset_name]
    context.problem_set_title = problem_set_title
    context.can_submit = psets[pset_name].status != "Closed"
    context.problem = problem
    context.psets = psets
    context.d = frappe.form_dict
    context.latest_submission = solution
    context.data = {
        "problem_set": psets[pset_name].problem_set,
        "problem": problem.name,
        "training": training_name,
        "submission_json": solution and solution.test_result or "null"
    }

    context.title = problem.title
