from django.urls import reverse
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        is_authenticated = self.request.user.is_authenticated
        context["is_authenticated"] = is_authenticated
        context["dashboard_url"] = reverse("feedback_list")
        context["analytics_url"] = reverse("analytics")
        context["login_url"] = reverse("account:user_login")
        context["register_url"] = reverse("account:user_register")

        context["hero_stats"] = [
            {"value": "24/7", "label": "feedback visibility"},
            {"value": "3", "label": "core workflows"},
            {"value": "1", "label": "shared source of truth"},
        ]
        context["feature_cards"] = [
            {
                "icon": "inbox",
                "title": "Track requests in one place",
                "description": "Collect feedback, route it to the right team, and keep every conversation visible.",
            },
            {
                "icon": "hub",
                "title": "Route by department and role",
                "description": "Managers, auditors, and owners get the access they need without manual follow-up.",
            },
            {
                "icon": "show_chart",
                "title": "See progress without guesswork",
                "description": "Monitor status, response times, and resolution trends from a clean dashboard.",
            },
        ]
        context["workflow_steps"] = [
            "Submit feedback from a simple form.",
            "Assign it to the right department automatically.",
            "Respond, track, and close the loop with visibility.",
        ]

        if is_authenticated:
            context["primary_action_label"] = "Open dashboard"
            context["primary_action_url"] = context["dashboard_url"]
            context["secondary_action_label"] = "View analytics"
            context["secondary_action_url"] = context["analytics_url"]
        else:
            context["primary_action_label"] = "Sign in"
            context["primary_action_url"] = context["login_url"]
            context["secondary_action_label"] = "Create account"
            context["secondary_action_url"] = context["register_url"]

        return context
