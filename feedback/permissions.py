from importlib import import_module
from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.db.models import QuerySet

if TYPE_CHECKING:
    from .models import Feedback


def _guardian_shortcuts():
    return import_module("guardian.shortcuts")


def sync_feedback_view_permissions(feedback: "Feedback") -> None:
    """Synchronize object-level view permission for one feedback item."""
    shortcuts = _guardian_shortcuts()
    assign_perm = shortcuts.assign_perm
    from .models import FeedbackResponderRecord

    # Creator always keeps access to their own feedback.
    assign_perm("feedback.view_feedback", feedback.creator, feedback)

    # Assigned responders can access feedback they are working on.
    assigned_responder_ids = FeedbackResponderRecord.objects.filter(
        feedback=feedback
    ).values_list("responder_id", flat=True)
    User = get_user_model()
    responders = User.objects.filter(id__in=assigned_responder_ids, is_active=True)
    for responder in responders:
        assign_perm("feedback.view_feedback", responder, feedback)

    # Department managers of the routed departments can access this feedback.
    manager_users = User.objects.filter(
        is_active=True,
        groups__name="Department Manager",
        department__in=feedback.to_departments.all(),
    ).distinct()
    for manager in manager_users:
        assign_perm("feedback.view_feedback", manager, feedback)


def get_feedback_queryset_for_user(user, base_queryset: QuerySet | None = None):
    """Return the feedback queryset visible to a user using Guardian object perms."""
    from .models import Feedback

    queryset = base_queryset or Feedback.objects.all()

    if user.is_superuser:
        return queryset

    get_objects_for_user = _guardian_shortcuts().get_objects_for_user
    return get_objects_for_user(
        user,
        "feedback.view_feedback",
        klass=queryset,
        use_groups=True,
        any_perm=False,
        accept_global_perms=False,
        with_superuser=False,
    )

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

