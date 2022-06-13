from collections import defaultdict

import frappe


class Status:
    UPCOMING = "Upcoming"
    ACTIVE = "Active"
    ARCHIVED = "Archived"


def get_context(context):
    trainings = unique(get_trainings_by_trainer(frappe.session.user) + get_trainings_by_participant(frappe.session.user))
    trainings.sort(key=lambda t: t.begin_date)

    trainings_by_status = split_trainings_by_status(trainings)

    context.trainings = trainings_by_status


def get_trainings_by_trainer(trainer):
    """Get trainings by trainer's user ID (i.e. email)"""

    training_names = frappe.get_all(
        "Training Trainer",
        filters={"user": frappe.session.user, "parenttype": "Training"},
        pluck="parent")

    trainings = [frappe.get_doc("Training", training_name) for training_name in training_names]
    for t in trainings:
        t.as_trainer = True

    return trainings


def get_trainings_by_participant(participant):
    training_names = frappe.get_all(
        "Training Participant",
        filters={"user": frappe.session.user, "parenttype": "Training"},
        pluck="parent")

    trainings = [frappe.get_doc("Training", training_name) for training_name in training_names]

    return trainings


def split_trainings_by_status(trainings):
    result = defaultdict(list)

    for training in trainings:
        result[training.status].append(training)

    return result


def unique(ls):
    return list(set(ls))
