from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import View
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from localhost.core.models import Property
from localhost.dashboard.forms import (PropertyForm, PropertyItemFormSet,
                                       PropertyImageFormSet)


class DashboardView(LoginRequiredMixin, View):
    pass


class ListingCreate(LoginRequiredMixin, CreateView):
    model = Property
    form_class = PropertyForm
    template_name = 'dashboard/listing/listing_create.html'
    success_url = reverse_lazy('dashboard:dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = PropertyImageFormSet(
                self.request.POST)
            context['property_item_formset'] = PropertyItemFormSet(
                self.request.POST)
        else:
            context['image_formset'] = PropertyImageFormSet()
            context['property_item_formset'] = PropertyItemFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        property_image_formset = context.get('image_formset')
        property_item_formset = context.get('property_item_formset')
        return super().form_valid(form)


class ListingUpdate(LoginRequiredMixin, UpdateView):
    model = Property
    form_class = PropertyForm


class ListingDelete(LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('dashboard:dashboard')
