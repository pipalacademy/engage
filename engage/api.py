import json
import frappe


@frappe.whitelist()
def get_problem_set_submissions():
    problem_set = frappe.form_dict["problem_set"]
    user = frappe.form_dict.get("user") or frappe.session.user
    result = frappe.db.get_list("Practice Problem Submission",
                                filters={
                                    "problem_set": problem_set,
                                    "owner": user
                                },
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
        raise frappe.exceptions.ValidationError(
            "author isn't the logged-in user")

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
        update_comment(problem_set=problem_set,
                       problem=p['problem'],
                       user=user,
                       comment=p['comment'],
                       correctness=p['correctness'],
                       clarity=p['clarity'])

    frappe.response["message"] = "done"


@frappe.whitelist()
def invite_participants():
    training = frappe.get_doc("Training", frappe.form_dict["training"])

    def get_data_as_tuples():
        invites = json.loads(frappe.form_dict["invites"])
        return ((invite["email"], invite["first_name"])
                for invite in invites)

    for email, first_name in get_data_as_tuples():
        if not frappe.db.exists("User", email):
            user = add_user(email, first_name)
        else:
            user = frappe.get_doc("User", email)

        training.add_participant(user, send_invitation_mail=True)
        training.save()

    return


def update_comment(problem_set,
                   problem,
                   user,
                   comment,
                   correctness=None,
                   clarity=None):
    result = frappe.get_list("Problem Review",
                             filters={
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
        update_comment(problem_set=problem_set,
                       problem=problem,
                       user=user,
                       comment=comment)


def add_user(email, first_name=None, last_name=None, send_welcome_mail=True):
    user = frappe.new_doc("User")
    user.update({
        "name": email,
        "email": email,
        "enabled": 1,
        "first_name": first_name or email,
        "last_name": last_name,
        "user_type": "Website User",
        "send_welcome_mail": 1 if send_welcome_mail else 0,
    })

    # not with ignore_permissions, since trainers would be system users
    user.insert()

    return user
