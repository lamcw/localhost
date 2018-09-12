from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import View
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from localhost.core.models import Property, PropertyImage, PropertyItemImage
from localhost.dashboard.forms import PropertyForm, PropertyItemFormSet


class DashboardView(LoginRequiredMixin, View):
    pass


class ListingCreate(LoginRequiredMixin, CreateView):
    model = Property
    form_class = PropertyForm
    template_name = 'dashboard/listing/listing_create.html'
    success_url = reverse_lazy('dashboard:dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['property_item_formset'] = PropertyItemFormSet(
            self.request.POST or None)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        property_item_formset = context.get('property_item_formset')
        form.instance.host = self.request.user
        if form.is_valid() and property_item_formset.is_valid():
            self.object = form.save()
            for img in self.request.FILES.getlist('property_img'):
                PropertyImage.objects.create(property=self.object, img=img)
            for form in property_item_formset:
                property_item = form.save(commit=False)
                property_item.property = self.object
                property_item.save()
                form.save_m2m()
                for img in self.request.FILES.getlist(form.prefix + '-img'):
                    PropertyItemImage.objects.create(
                        property_item=property_item, img=img)
        return super().form_valid(form)


class ListingUpdate(LoginRequiredMixin, UpdateView):
    model = Property
    form_class = PropertyForm
    success_url = reverse_lazy('dashboard:dashboard')


class ListingDelete(LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('dashboard:dashboard')
