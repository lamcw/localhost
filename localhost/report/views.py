from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView

from localhost.core.models import PropertyItem
from localhost.report.models import PropertyItemReport, UserReport

User = get_user_model()


class UserReportCreate(LoginRequiredMixin, CreateView):
    model = UserReport
    success_url = reverse_lazy('core:index')
    template_name = 'report/user_report_create.html'
    fields = ('description', )

    def form_valid(self, form):
        form.instance.from_user = self.request.user
        form.instance.reported_user = get_object_or_404(
            User, pk=self.kwargs.get('pk'))
        return super().form_valid(form)


class PropertyItemReportCreate(LoginRequiredMixin, CreateView):
    model = PropertyItemReport
    template_name = 'report/property_report_create.html'
    fields = ('description', )

    def form_valid(self, form):
        form.instance.from_user = self.request.user
        form.instance.property_item = get_object_or_404(
            PropertyItem, pk=self.kwargs.get('pk'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'core:property-detail', kwargs={'pk': self.kwargs.get('pk')})
