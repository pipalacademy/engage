from collections import defaultdict

import frappe


class Status:
    UPCOMING = "Upcoming"
    ACTIVE = "Active"
    ARCHIVED = "Archived"


def get_context(context):
    if frappe.session.user == "Guest":
        context.template = "www/redirect_to_login.html"
        return

    trainings = unique_trainings(get_trainings_by_trainer(frappe.session.user) + get_trainings_by_participant(frappe.session.user))
    trainings.sort(key=lambda t: t.begin_date)

    trainings_by_status = split_trainings_by_status(trainings)

    context.trainings = trainings_by_status


def get_trainings_by_trainer(trainer):
    """Get trainings by trainer's user ID (i.e. email)"""

    training_names = frappe.get_all(
        "Training Trainer",
        filters={"user": trainer, "parenttype": "Training"},
        pluck="parent")

    trainings = [frappe.get_doc("Training", training_name) for training_name in training_names]
    for t in trainings:
        t.as_trainer = True

    return trainings


def get_trainings_by_participant(participant):
    training_names = frappe.get_all(
        "Training Participant",
        filters={"user": participant, "parenttype": "Training"},
        pluck="parent")

    trainings = [frappe.get_doc("Training", training_name) for training_name in training_names]

    return trainings


def split_trainings_by_status(trainings):
    result = defaultdict(list)

    for training in trainings:
        result[training.status].append(training)

    return result


def unique_trainings(trainings):
    # convert to dict with key we want to check uniqueness with, then back
    return list({t.name: t for t in trainings}.values())
