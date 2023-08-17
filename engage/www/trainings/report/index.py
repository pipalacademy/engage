import frappe

from engage.utils import with_training, require_login, require_trainer_role


@require_login
@with_training
@require_trainer_role
def get_context(context, training):
    context.training = training

    participants = [p.user for p in training.participants]
    participant_full_names = {
        username: get_full_name(username)
        for username in participants
    }

    # sort by full name
    participants.sort(key=lambda x: participant_full_names[x].lower())

    problem_sets = [pset.problem_set for pset in training.problem_sets]
    problem_set_titles = {
        pset.problem_set: pset.title
        for pset in training.problem_sets
    }

    submissions = get_submissions_for_training(training.name)
    submissions_dict = group_submissions_by_participant_and_problem_set(
        submissions)

    def get_header_columns():
        name_header = ["Name"]

        pset_problem_count = [get_problem_count(pset) for pset in problem_sets]
        score_headers = [
            f"{problem_set_titles[pset]} ({problem_count})"
            for pset, problem_count in zip(problem_sets, pset_problem_count)
        ]
        total_header = [f"Total ({sum(pset_problem_count)})"]

        return name_header + score_headers + total_header

    def get_row(participant):
        user_submissions = submissions_dict.get(participant, {})

        name_column = [participant_full_names[participant]]
        score_columns = [
            sum(1 for s in user_submissions.get(pset, []) if s.get('outcome') == 'passed') for pset in problem_sets
        ]
        total_score_column = [sum(score_columns)]
        return name_column + score_columns + total_score_column

    context.columns = get_header_columns()
    context.rows = [get_row(participant) for participant in participants]


def get_submissions_for_training(training_name):
    doctype = "Practice Problem Submission"
    return frappe.get_all(doctype,
                          fields="*",
                          filters={
                              "training": training_name,
                              "test_outcome": "passed"
                          },
                          group_by="problem, author")


def get_full_name(username):
    user = frappe.get_cached_doc("User", username)
    return user.full_name


def get_problem_count(pset_name):
    return frappe.db.count("Problem Reference",
                           filters={
                               "parenttype": "Problem Set",
                               "parent": pset_name
                           })


def group_submissions_by_participant_and_problem_set(submissions):
    submissions_dict = {}
    for submission in submissions:
        author, problem_set = submission["author"], submission["problem_set"]
        submissions_dict.setdefault(author, {})
        submissions_dict[author].setdefault(problem_set, [])
        submissions_dict[author][problem_set].append(submission)

    return submissions_dict
