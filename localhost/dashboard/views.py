from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, ListView, UpdateView,
                                  View)

from localhost.core.models import (Booking, Property, PropertyImage,
                                   PropertyItemImage)
from localhost.core.views import FormListView
from localhost.dashboard.forms import (PropertyForm, PropertyItemFormSet,
                                       PropertyItemReviewForm)


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
            self.request.POST or None, self.request.FILES or None)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        property_item_formset = context.get('property_item_formset')
        if form.is_valid() and property_item_formset.is_valid():
            form.instance.host = self.request.user
            self.object = form.save()
            for img in self.request.FILES.getlist('img'):
                PropertyImage.objects.create(property=self.object, img=img)
            for form in property_item_formset:
                property_item = form.save(commit=False)
                property_item.property = self.object
                property_item.save()
                form.save_m2m()
                for img in self.request.FILES.getlist(form.prefix + '-img'):
                    PropertyItemImage.objects.create(
                        property_item=property_item, img=img)
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class ListingUpdate(LoginRequiredMixin, UpdateView):
    model = Property
    form_class = PropertyForm
    success_url = reverse_lazy('dashboard:dashboard')


class ListingDelete(LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('dashboard:dashboard')


class BookingListView(LoginRequiredMixin, FormListView):
    model = Booking
    form_class = PropertyItemReviewForm
    template_name = 'dashboard/booking_list.html'

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)
