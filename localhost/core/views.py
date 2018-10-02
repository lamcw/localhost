import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Avg, F, Q
from django.utils import dateparse, timezone
from django.views.generic import DetailView, ListView

from localhost.core.models import (Bid, BiddingSession, Property,
                                   PropertyItemReview)
from localhost.core.utils import parse_address

logger = logging.getLogger(__name__)


class PropertyDetailView(DetailView):
    queryset = Property.objects.prefetch_related('property_item')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        property = self.get_object()
        property_item = property.property_item.all()[0]
        if property_item:
            context['session_end'] = property_item.current_session.end_time
        return context

    def get_object(self, queryset=None):
        property = super().get_object(queryset)
        # note that this is extremely inefficient, as the db hits grows
        # linearly. A more sophisticated method is needed.
        for property_item in property.property_item.all():
            reviews = PropertyItemReview.objects.filter(
                booking__property_item=property_item)
            property_item.reviews = reviews.order_by('-rating')
            property_item.rating = reviews.aggregate(
                Avg('rating'))['rating__avg']
            now = timezone.localtime()
            qs1 = BiddingSession.objects.filter(
                Q(start_time__lte=F('end_time')),
                Q(start_time__lte=now),
                end_time__gte=now,
                propertyitem=property_item)
            qs2 = BiddingSession.objects.filter(
                Q(start_time__gt=F('end_time')),
                Q(start_time__lte=now)
                | Q(end_time__gte=now),
                propertyitem=property_item)
            property_item.current_session = qs1.union(qs2).first()
            try:
                property_item.current_price = property_item.bids.latest().amount
                property_item.has_bid = True
                property_item.highest_bidder = property_item.bids.latest().bidder
            except Bid.DoesNotExist:
                property_item.current_price = property_item.min_price
                property_item.has_bid = False
        return property


class SearchResultsView(ListView):
    model = Property
    template_name = 'core/search_results.html'
    paginate_by = 20

    def get_queryset(self, **kwargs):
        args = self.request.GET

        try:
            latitude = float(args.get('lat', settings.DEFAULT_SEARCH_COORD[0]))
            longitude = float(
                args.get('lng', settings.DEFAULT_SEARCH_COORD[1]))
        except ValueError:
            address = args.get('address')
            if address:
                latitude, longitude = parse_address(address)
            else:
                # address also empty
                latitude, longitude = parse_address(
                    settings.DEFAULT_SEARCH_ADDRESS)

        guests = int(args.get('guests', 1))
        bid_now = args.get('bidding-active', 'off')
        # default checkin time is set half an hour from now
        default_checkin = (
            timezone.now() + timedelta(minutes=30)).strftime('%H:%M')
        checkin = dateparse.parse_time(args.get('checkin', default_checkin))

        properties = self.model.objects.within(latitude, longitude)

        if bid_now == 'on':
            now = timezone.localtime()

            # filter if checkin times are on same day
            qs1 = properties.filter(
                Q(earliest_checkin_time__lte=F('latest_checkin_time')),
                Q(earliest_checkin_time__lte=checkin),
                latest_checkin_time__gt=checkin)

            # filter if checkin times cross midnight
            qs2 = properties.filter(
                Q(earliest_checkin_time__gt=F('latest_checkin_time')),
                Q(earliest_checkin_time__lte=checkin)
                | Q(latest_checkin_time__gt=checkin))

            qs3 = properties.filter(
                Q(property_item__session__start_time__lte=F('end_time')),
                Q(property_item__session__start_time__lte=now),
                property_item__session__end_time__gte=now)

            qs4 = (properties.filter(
                Q(property_item__session__start_time__gt=F('end_time')),
                Q(property_item__session__start_time__lte=now)
                | Q(property_item__session__end_time__gte=now)))

            properties = (qs1 | qs2) & (qs3 | qs4).filter(
                property_item__session__end_time__gt=now,
                property_item__session__start_time__lte=now,
                property_item__available=True,
                property_item__capacity__gte=guests).distinct()

        return properties.order_by('distance')


class ProfileView(DetailView):
    model = get_user_model()
    template_name = 'core/public_profile.html'
    context_object_name = 'user'
