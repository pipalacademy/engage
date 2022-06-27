# import frappe

from engage.utils import require_login, require_trainer_role, with_training


@require_login
@with_training
@require_trainer_role
def get_context(context, training):
    context.training = training
