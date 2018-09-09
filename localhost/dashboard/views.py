from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import View
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from localhost.core.models import Property
from localhost.dashboard.forms import (PropertyForm, PropertyImageFormSet,
                                       PropertyItemFormSet)


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
            context['image_formset'] = PropertyImageFormSet(self.request.POST)
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
        if all([
                form.is_valid(),
                property_image_formset.is_valid(),
                property_item_formset.is_valid()
        ]):
            self.object = form.save(commit=False)
            self.object.host = self.request.user
            form.save()
            form.save_m2m()
            for form in property_image_formset:
                image = form.save(commit=False)
                image.property = self.object
                form.save()
            for form in property_item_formset:
                property_item = form.save(commit=False)
                property_item.property = self.object
                property_item = form.save()
                form.save_m2m()
                for image_form in form.image_formset:
                    image = image_form.save(commit=False)
                    image.property_item = property_item
                    image_form.save()
        return super().form_valid(form)


class ListingUpdate(LoginRequiredMixin, UpdateView):
    model = Property
    form_class = PropertyForm


class ListingDelete(LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('dashboard:dashboard')
