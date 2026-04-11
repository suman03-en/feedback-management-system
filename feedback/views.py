from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    DeleteView,
    UpdateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.db.models import Q

from .models import (
    Feedback,
    FeedbackResponse,
    FeedbackResponderRecord,
    Department,
)
from .forms import (
    FeedbackForm,
    FeedbackResponseForm,
    FeedbackResponseAssignForm,
)
from .mixins import FeedbackMixin


def user_can_manage_feedback(feedback, user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if not user.is_staff:
        return False
    return feedback.to_departments.filter(name=user.department).exists()


class FeedbackListView(LoginRequiredMixin, ListView):
    model = Feedback
    template_name = "feedback/feedback_list.html"
    context_object_name = "feedbacks"

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.is_staff:
            return Feedback.objects.all().order_by("-created_at")
        elif FeedbackResponderRecord.objects.filter(
            feedback__in=Feedback.objects.all(),
            responder=self.request.user
        ).exists():
            return Feedback.objects.filter(
                Q(creator=self.request.user) |
                Q(feedbackresponderrecord__responder=self.request.user)
            ).distinct().order_by("-created_at")
        return Feedback.objects.filter(creator=self.request.user).order_by("-created_at")


class FeedbackDetailView(LoginRequiredMixin, DetailView):
    model = Feedback
    template_name = "feedback/feedback_detail.html"
    context_object_name = "feedback"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        feedback = context["feedback"]
        context["can_assign_feedback"] = user_can_manage_feedback(
            feedback, self.request.user
        )
        if context["can_assign_feedback"]:
            context["assign_form"] = FeedbackResponseAssignForm(
                feedback=feedback,
                assigner=self.request.user,
            )
        return context


class FeedbackCreateView(LoginRequiredMixin, CreateView):
    model = Feedback
    template_name = "feedback/feedback_form.html"
    form_class = FeedbackForm

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)


class FeedbackDeleteView(DeleteView):
    model = Feedback
    template_name = "feedback/feedback_confirm_delete.html"
    success_url = reverse_lazy("feedback_list")


class FeedbackResponseCreateView(LoginRequiredMixin, CreateView):
    model = FeedbackResponse
    template_name = "feedback/feedback_response_form.html"
    form_class = FeedbackResponseForm
    success_url = reverse_lazy("feedback_list")

    def get_feedback(self):
        """Helper method to retrieve the associated feedback based on the URL parameter."""
        return Feedback.objects.get(id=self.kwargs.get("pk"))

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        self.feedback = self.get_feedback()
        is_assigned = FeedbackResponderRecord.objects.filter(
            feedback=self.feedback,
            responder=request.user,
        ).exists()
        if not is_assigned:
            raise PermissionDenied("You are not assigned to this feedback.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["feedback"] = self.feedback
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["feedback"] = self.feedback
        return kwargs

    def form_valid(self, form):
        self.object = form.save(responder=self.request.user)
        return redirect(self.get_success_url())


class FeedbackResponseListView(LoginRequiredMixin, FeedbackMixin, ListView):
    model = FeedbackResponse
    template_name = "feedback/feedback_response_list.html"
    context_object_name = "responses"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["feedback"] = self.get_feedback()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["feedback"] = self.get_feedback()
        return kwargs

    def get_queryset(self):
        feedback_id = self.kwargs.get("pk")
        return FeedbackResponse.objects.filter(feedback__id=feedback_id).order_by(
            "-created_at"
        )


class FeedbackResponseEditView(LoginRequiredMixin, UpdateView):
    model = FeedbackResponse
    template_name = "feedback/feedback_response_form.html"
    form_class = FeedbackResponseForm
    pk_url_kwarg = "pk"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["feedback"] = self.object.feedback
        return kwargs

    def get_success_url(self):
        return reverse("feedback_response_list", kwargs={"pk": self.object.feedback.pk})


class FeedbackResponseDeleteView(LoginRequiredMixin, DeleteView):
    model = FeedbackResponse
    template_name = "feedback/feedback_response_confirm_delete.html"
    success_url = reverse_lazy("feedback_list")


class FeedbackResponseAssignView(LoginRequiredMixin, View):
    form_class = FeedbackResponseAssignForm
    template_name = "feedback/feedback_assign_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.feedback = get_object_or_404(Feedback, pk=kwargs.get("pk"))
        if not user_can_manage_feedback(self.feedback, request.user):
            raise PermissionDenied("You are not allowed to assign this feedback.")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        form = self.form_class(feedback=self.feedback, assigner=request.user)
        return render(
            request,
            self.template_name,
            {"form": form, "feedback": self.feedback},
        )

    def post(self, request, pk):
        form = self.form_class(
            request.POST, feedback=self.feedback, assigner=request.user
        )
        if form.is_valid():
            responder = form.cleaned_data["responder"]
            self.feedback.assign_to_responder(responder)
            return redirect("feedback_response_list", pk=self.feedback.pk)

        return render(
            request,
            self.template_name,
            {"form": form, "feedback": self.feedback},
        )
    

#additinal view to add the department , only allowed to superuser and staff user
class DepartmentCreateView(LoginRequiredMixin, CreateView):
    model = Department
    template_name = "feedback/department_form.html"
    fields = ["name", "description"]
    success_url = reverse_lazy("feedback_list")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (request.user.is_superuser or request.user.is_staff):
            raise PermissionDenied("You do not have permission to add a department.")
        return super().dispatch(request, *args, **kwargs)
