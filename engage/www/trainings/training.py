import frappe

from engage.utils import require_login, with_training


@require_login
@with_training
def get_context(context, training):
    context.t = training
    context.title = training.title

    context.participant = member = get_member(training, frappe.session.user)
    if member and member.is_trainer:
        training.can_review = True
        training.can_invite = True

    if not member:
        return

    if training.refresh_problem_sets():
        training.save(ignore_permissions=True)
        frappe.db.commit()

    problem_sets = [
        pset for pset in training.problem_sets if pset.is_published
    ]

    context.problem_sets = problem_sets[::-1]
    context.submissions = get_user_submissions(training.name, member.user)


def get_user_submissions(training: str, user: str):
    user_submissions_list = frappe.get_all(
        "Practice Problem Latest Submission",
        filters={
            "training": training,
            "author": user
        },
        fields=["name", "problem_set", "problem", "test_outcome"],
        page_length=1000)

    comment_counts = get_comment_counts(training, user)
    for doc in user_submissions_list:
        doc['comments'] = comment_counts.get(doc.name)
    return {sub["problem"]: sub for sub in user_submissions_list}

def get_comment_counts(training, user):
    q = """
    SELECT doc.name, count(r.name) as count
    FROM `tabPractice Problem Latest Submission` as doc
    LEFT OUTER JOIN `tabDiscussion Topic` as t ON  t.reference_doctype='Practice Problem Latest Submission' AND t.reference_docname=doc.name
    LEFT OUTER JOIN `tabDiscussion Reply` as r ON r.topic=t.name
    WHERE doc.author="%(user)s" and training="%(training)s"
    GROUP BY doc.name"""
    values = {"user": user, "training": training}
    rows = frappe.db.sql(q, values=values, as_dict=True)
    return {row.name: row.count for row in rows}


def time_is_between(val, lesser, greater):
    return lesser <= val and val <= greater


def get_member(training, username):
    for p in training.participants:
        if p.user == username:
            p.is_trainer = training.has_user_as_trainer(p.user)
            return p

    for t in training.trainers:
        if t.user == username:
            t.is_trainer = True
            t.jh_username = getattr(t, "jh_username", None)
            t.jh_password = getattr(t, "jh_password", None)
            return t

    return
