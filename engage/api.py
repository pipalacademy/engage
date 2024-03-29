import json
import frappe
from functools import wraps
from math import ceil
from werkzeug.wrappers import Response

from engage.livecode import run_tests
from engage.utils import get_submissions_with_listing_fields as _get_submissions, get_submissions_count

SUBMISSIONS_PAGE_LENGTH = 60


def with_pagination_params(fn):

    @wraps(fn)
    def wrapper(*args, **kwargs):
        pagination_params = get_pagination_parameters_from_form_dict(
            frappe.form_dict)
        return fn(*args, **kwargs, pagination_params=pagination_params)

    return wrapper


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
@with_pagination_params
def get_submissions(training,
                    problem_set=None,
                    problem=None,
                    author=None,
                    for_review=None,
                    test_outcome=None,
                    pagination_params=None):
    if not is_trainer(training, frappe.session.user):
        return Response(status=404)

    filters = {}

    update_if(filters, {
        "problem_set": problem_set,
        "problem": problem,
        "author": author
    }, lambda x: x is not None)

    if for_review is not None:
        for_review = True if for_review and for_review not in {"0", "false"
                                                               } else False
        filters.update(for_review=for_review)

    if test_outcome is not None:
        assert test_outcome in {
            "passed", "failed"
        }, "test_outcome must be one of: 'passed', 'failed'"
        filters.update(test_outcome=test_outcome)

    submissions = _get_submissions(training,
                                   filters=filters,
                                   **pagination_params)
    total_count = get_submissions_count(training, filters=filters)
    total_pages = ceil(total_count / SUBMISSIONS_PAGE_LENGTH)

    frappe.response["message"] = {
        "ok": True,
        "submissions": submissions,
        "total_pages": total_pages
    }


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

    result = run_tests(problem, code)
    test_outcome = result["ok"] and result["outcome"] or None
    test_result = result["ok"] and json.dumps(result) or None

    doc = frappe.get_doc({
        "problem_set": problem_set,
        "problem": problem,
        "code": code,
        "author": author,
        "training": training,
        "test_outcome": test_outcome,
        "test_result": test_result,
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
        return ((invite["email"], invite["first_name"]) for invite in invites)

    for email, first_name in get_data_as_tuples():
        if not frappe.db.exists("User", email):
            user = add_user(email, first_name)
        else:
            user = frappe.get_doc("User", email)

        training.add_participant(user, send_invitation_mail=True)
        training.save()

    return


@frappe.whitelist()
def update_problem_sets():
    training = frappe.get_doc("Training", frappe.form_dict["training"])
    problem_sets = frappe.form_dict["problem_sets"]

    def get_pset_name(training_name, pset_slug):
        return f"{training_name.replace('/', '-')}-{pset_slug}"

    result = {}

    keep_problem_sets = []
    for pset in problem_sets:
        slug = pset["slug"]
        title = pset["title"]
        published = bool(pset["published"])
        problem_names = pset["problems"]

        pset_name = get_pset_name(training_name=training.name, pset_slug=slug)
        try:
            pset_doc = frappe.get_doc("Problem Set", pset_name)
        except frappe.exceptions.DoesNotExistError:
            # if not pset_doc:
            pset_doc = frappe.get_doc({"doctype": "Problem Set", "title": title, "published": published})
            pset_doc.insert()
            frappe.rename_doc("Problem Set", pset_doc.name, pset_name)
            pset_doc = frappe.get_doc("Problem Set", pset_name)

        old_problem_names = [p_ref.problem for p_ref in pset_doc.problems]

        additions = [name for name in problem_names if name not in old_problem_names]
        deletions = [p_ref for p_ref in pset_doc.problems if p_ref.problem not in problem_names]

        result[slug] = {"+": len(additions), "-": len(deletions)}

        for ref in deletions:
            pset_doc.remove(ref)
            ref.delete()

        for p_name in additions:
            if not frappe.db.exists("Practice Problem", p_name):
                frappe.response["result"] = f"Problem {p_name} not found"
                raise Exception(f"Problem {p_name} not found")
            pset_doc.append(
                "problems",
                frappe.get_doc({"doctype": "Problem Reference", "problem": p_name})
           )

        pset_doc.save()

        for p_ref in pset_doc.problems:
            p_ref.idx = problem_names.index(p_ref.problem) + 1

        pset_doc.save()
        keep_problem_sets.append(pset_doc)

    old_pset_names = [pset_ref.problem_set for pset_ref in training.problem_sets]
    new_pset_names = [pset_doc.name for pset_doc in keep_problem_sets]

    additions = [
        pset for pset in keep_problem_sets if pset.name not in old_pset_names
    ]
    deletions = [
        pset_ref for pset_ref in training.problem_sets if pset_ref.problem_set not in new_pset_names
    ]

    for pset_ref in deletions:
        pset_doc = frappe.get_doc("Problem Set", pset_ref.problem_set)
        training.remove(pset_ref)
        training.save()
        pset_doc.delete()

        result[pset_ref.slug] = {"op": "deleted"}

    for pset_doc in additions:
        pset_ref = frappe.get_doc({
            "doctype": "Problem Set Reference",
            "problem_set": pset_doc.name,
            "status": "Published" if pset_doc.published else "Pending",
            "slug": pset_doc.name.removeprefix(f"{training.name.replace('/', '-')}-"),
        })
        training.append("problem_sets", pset_ref)

        result[pset_ref.slug]["op"] = "added"

    training.save()

    for pset_ref in training.problem_sets:
        pset_ref.idx = new_pset_names.index(pset_ref.problem_set) + 1

    training.save()
    frappe.response["result"] = result


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


def get_pagination_parameters_from_form_dict(d):
    page = get_current_page(d)
    start = (page - 1) * SUBMISSIONS_PAGE_LENGTH

    return dict(page_length=SUBMISSIONS_PAGE_LENGTH, start=start)


def get_current_page(d):
    return int(d.page) if "page" in d else 1


def is_trainer(training_name, user):
    return frappe.db.exists({
        "doctype": "Training Trainer",
        "parenttype": "Training",
        "parent": training_name,
        "user": user
    })


def update_if(d1, d2, condition):
    for key, val in d2.items():
        if condition(val):
            d1.update({key: val})
