from .models import Feedback


class FeedbackMixin:
    """Mixin to provide common functionality for feedback-related views."""

    def get_feedback(self):
        """Helper method to retrieve the associated feedback based on the URL parameter."""

        return Feedback.objects.get(id=self.kwargs.get("pk"))
    


