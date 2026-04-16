from django.core.management.base import BaseCommand

from feedback.models import Feedback
from feedback.permissions import sync_feedback_view_permissions


class Command(BaseCommand):
    help = (
        "Sync Guardian object-level feedback view permissions for all feedback records"
    )

    def handle(self, *args, **options):
        total = 0
        for feedback in Feedback.objects.prefetch_related(
            "to_departments", "feedback_responder_records"
        ).select_related("creator"):
            sync_feedback_view_permissions(feedback)
            total += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Synced object permissions for {total} feedback record(s)."
            )
        )
