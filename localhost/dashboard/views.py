from datetime import datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import (BooleanField, Case, Exists, F, Max, OuterRef,
                              Subquery, Value, When)
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, FormView, ListView,
                                  UpdateView)

from localhost.core.models import (Bid, Booking, Property, PropertyImage,
                                   PropertyItem, PropertyItemImage,
                                   PropertyItemReview)
from localhost.dashboard.forms import (PropertyForm, PropertyItemFormSet,
                                       WalletForm)


class ProfileView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    fields = ('bio', )
    template_name = 'dashboard/profile.html'
    success_url = reverse_lazy('dashboard:profile')

    def get_object(self):
        return self.request.user


class ActiveBidsView(LoginRequiredMixin, ListView):
    model = PropertyItem
    context_object_name = 'property_items'
    template_name = 'dashboard/active_bids.html'

    def get_queryset(self, **kwargs):
        # uses order_by() instead of latest() since latest() evaluates the expr
        user_bid = Bid.objects.filter(
            property_item=OuterRef('pk'),
            bidder=self.request.user).order_by('amount')
        return PropertyItem.objects \
            .filter(bids__bidder=self.request.user).distinct() \
            .annotate(current_bid=Max('bids__amount')) \
            .annotate(user_bid=Subquery(user_bid.values('amount')[:1]))


class WalletView(LoginRequiredMixin, FormView):
    form_class = WalletForm
    template_name = 'dashboard/wallet.html'
    success_url = reverse_lazy('dashboard:wallet')

    def form_valid(self, form):
        recharge = form.cleaned_data.get('recharge_amount')
        self.request.user.credits = F('credits') + recharge
        self.request.user.save()
        return super().form_valid(form)


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
                booking.latest_checkin_time,
                time(tzinfo=timezone.get_current_timezone())) + timedelta(
                    days=1)
            if timezone.now() >= date_at_least:
                return super().dispatch(request, *args, **kwargs)
            else:
                return self.handle_no_permission()


class ListingListView(LoginRequiredMixin, ListView):
    model = Property
    template_name = 'dashboard/property_listings.html'

    def get_queryset(self, **kwargs):
        return Property.objects.prefetch_related().filter(
            host=self.request.user)


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
    template_name = 'dashboard/booking_history.html'

    def get_queryset(self):
        """
        Return a QuerySet of Booking annotated with:

        1. reviewed: if a booking is reviewed by the user
        2. passed_one_day: True if a day has passed since the booking date
        3. can_cancel: True if the user can cancel this booking
        """
        reviews = PropertyItemReview.objects.filter(
            booking=OuterRef('pk'), booking__user=self.request.user)
        # today >= booking.latest_checkin_time.date + 1 day
        # so latest_checkin_time <= today - 1 day
        one_day_ago = timezone.now() - timedelta(days=1)
        return Booking.objects.prefetch_related() \
            .filter(user=self.request.user) \
            .order_by('-earliest_checkin_time') \
            .annotate(reviewed=Exists(reviews)) \
            .annotate(passed_one_day=Case(
                When(latest_checkin_time__lte=one_day_ago, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )) \
            .annotate(can_cancel=Case(
                When(
                    earliest_checkin_time__gt=timezone.now(),
                    then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            ))


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
