import frappe

@frappe.whitelist()
def get_problem_set_submissions():
    problem_set = frappe.form_dict["problem_set"]
    user = frappe.form_dict.get("user") or frappe.session.user
    result = frappe.db.get_list(
        "Practice Problem Submission", 
        filters={"problem_set": problem_set, "owner": user}, 
        fields=["problem", "code", "creation"],
        order_by="creation",
        page_length=10000)
        
    solutions = {row.problem: row for row in result}

    frappe.response["message"] = solutions


@frappe.whitelist()
def submit_practice_problem():
    problem_set = frappe.form_dict["problem_set"]
    problem = frappe.form_dict["problem"]
    code = frappe.form_dict["code"]
    author = frappe.form_dict.get("user") or frappe.session.user
    training = frappe.form_dict["training"]

    if author != frappe.session.user:
        raise frappe.exceptions.ValidationError("author isn't the logged-in user")

    doc = frappe.get_doc({
        "problem_set": problem_set,
        "problem": problem,
        "code": code,
        "author": author,
        "training": training,
        "doctype": "Practice Problem Submission"
    }).insert(ignore_permissions=True)

    frappe.response["message"] = doc.as_dict()


@frappe.whitelist()
def problem_set_update_comments():
    problem_set = frappe.form_dict["problem_set"]
    user = frappe.form_dict.get("user")

    problems = json.loads(frappe.form_dict['problems'])

    for p in problems:
        update_comment(
            problem_set=problem_set, 
            problem=p['problem'], 
            user=user, 
            comment=p['comment'], 
            correctness=p['correctness'],
            clarity=p['clarity'])

    frappe.response["message"] = "done"


def update_comment(problem_set, problem, user, comment, correctness=None, clarity=None):
    result = frappe.get_list("Problem Review", filters={
        "problem_set": problem_set,
        "problem": problem,
        "user": user
    })
    name = result and result[0] or None
    if not name:
        return False
    doc = frappe.get_doc("Problem Review", name)
    doc.comment = comment
    if correctness is not None:
        doc.correctness = correctness or None
    if clarity is not None:
        doc.clarity = clarity or None
    doc.save()


def update_comments(problem_set, user, comments):
    for problem, comment in comments.items():
        update_comment(problem_set=problem_set, problem=problem, user=user, comment=comment)
