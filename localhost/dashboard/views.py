from datetime import datetime, time, timedelta

from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, ListView, UpdateView,
                                  TemplateView)

from localhost.core.models import (Booking, Property, PropertyImage,
                                   PropertyItemImage, PropertyItemReview)
from localhost.dashboard.forms import PropertyForm, PropertyItemFormSet


class PropertyItemReviewMixin(AccessMixin):
    """
    Allow access only if property item review does not exists,
    and the date today is the day after booking.

    URL has to contain <int:pk>
    """
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        try:
            PropertyItemReview.objects.get(booking=kwargs.get('pk'))
            return self.handle_no_permission()
        except ObjectDoesNotExist:
            booking = Booking.objects.get(pk=kwargs.get('pk'))
            # next day after the booking
            date_at_least = datetime.combine(
                booking.date,
                time(tzinfo=timezone.get_current_timezone())) + timedelta(
                    days=1)
            if timezone.now() >= date_at_least:
                return super().dispatch(request, *args, **kwargs)
            else:
                return self.handle_no_permission()

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'

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


class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'dashboard/booking_list.html'

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)


class ListingReviewView(LoginRequiredMixin, PropertyItemReviewMixin,
                        CreateView):
    model = PropertyItemReview
    success_url = reverse_lazy('dashboard:booking-history')
    fields = (
        'rating',
        'description',
    )
    template_name = 'dashboard/property_item_review.html'

    def form_valid(self, form):
        form.instance.booking = Booking.objects.get(id=self.kwargs.get('pk'))
        return super().form_valid(form)
