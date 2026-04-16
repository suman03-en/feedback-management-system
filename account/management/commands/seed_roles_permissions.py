from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


# role -> (app_label, model, codename)
ROLE_PERMISSIONS = {
    "Employee": [
        ("feedback", "feedback", "add_feedback"),
        ("feedback", "feedback", "change_feedback"),
        ("feedback", "feedback", "view_feedback"),
    ],
    "Responder": [
        ("feedback", "feedback", "view_feedback"),
        ("feedback", "feedbackresponse", "add_feedbackresponse"),
        ("feedback", "feedbackresponse", "view_feedbackresponse"),
        ("feedback", "feedbackresponse", "change_feedbackresponse"),
    ],
    "Department Manager": [
        ("feedback", "feedback", "view_feedback"),
        ("feedback", "feedback", "assign_feedback"),  # custom Meta.permission
        ("feedback", "feedbackresponse", "view_feedbackresponse"),
    ],
    "Feedback Admin": [
        ("feedback", "feedback", "add_feedback"),
        ("feedback", "feedback", "change_feedback"),
        ("feedback", "feedback", "view_feedback"),
        ("feedback", "feedback", "delete_feedback"),
        ("feedback", "feedback", "assign_feedback"),  # custom
        ("feedback", "feedback", "revoke_responder"),  # custom
        ("feedback", "feedbackresponse", "add_feedbackresponse"),
        ("feedback", "feedbackresponse", "change_feedbackresponse"),
        ("feedback", "feedbackresponse", "view_feedbackresponse"),
        ("feedback", "feedbackresponse", "delete_feedbackresponse"),
        ("account", "user", "add_user"),
        ("account", "user", "change_user"),
        ("account", "user", "view_user"),
        ("account", "user", "delete_user"),
    ],
    "Auditor": [
        ("feedback", "feedback", "view_feedback"),
        ("feedback", "feedbackresponse", "view_feedbackresponse"),
    ],
}


class Command(BaseCommand):
    help = "Seed initial roles and permissions"

    def handle(self, *args, **options):
        for role_name, permission_specs in ROLE_PERMISSIONS.items():
            group, created = Group.objects.get_or_create(name=role_name)
            self.stdout.write(
                self.style.SUCCESS(f"Created role: {role_name}")
                if created
                else self.style.WARNING(f"Role already exists: {role_name}")
            )

            permissions = []
            for app_label, model, codename in permission_specs:
                try:
                    perm = Permission.objects.get(
                        content_type__app_label=app_label,
                        content_type__model=model,
                        codename=codename,
                    )
                    permissions.append(perm)
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Missing permission: {app_label}.{model}.{codename}"
                        )
                    )

            group.permissions.set(permissions)

        self.stdout.write(self.style.SUCCESS("Roles and permissions seeding completed."))