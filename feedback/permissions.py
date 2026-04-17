from importlib import import_module
from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.db.models import QuerySet

if TYPE_CHECKING:
    from .models import Feedback


def _guardian_shortcuts():
    """Helper function to import Guardian shortcuts only when needed.
    This avoids circular import issues since some permission functions are used in models.py
    """
    return import_module("guardian.shortcuts")

def assign_many_perms(perms, user, obj):
    """Assign multiple permissions to a user for a specific object."""
    shortcuts = _guardian_shortcuts()
    assign_perm = shortcuts.assign_perm

    for perm in perms:
        assign_perm(perm, user, obj)

def assign_owner_perms(user, obj, perms=None):
    """Assign owner permissions to a user for a specific object.
    
    Args:
        user: The user to assign permissions to.
        obj: The object for which permissions are being assigned.
        perms: Single permission or list of permissions to assign. if None, defaults to view, change, delete permissions for the object's model.

    """

    app_label = obj._meta.app_label
    model_name = obj._meta.model_name

    default_perms = perms or [
        f"{app_label}.view_{model_name}",
        f"{app_label}.change_{model_name}",
        f"{app_label}.delete_{model_name}",
    ]

    assign_many_perms(default_perms, user, obj)

def assign_department_permissions(feedback):
    # get all routed departments for this object, can be feedback or feedback response
    shortcuts = _guardian_shortcuts()
    assign_perm = shortcuts.assign_perm

    departments = feedback.to_departments.all()

    for department in departments:
        #assign view permission to the managers of  the routed departments
        for manager in department.managers.all():
            assign_perm("feedback.view_feedback", manager, feedback)

        #assign view permission to the auditors of  the routed departments
        for auditor in department.auditors.all():
            assign_perm("feedback.view_feedback", auditor, feedback)

