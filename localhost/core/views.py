import logging
from datetime import timedelta
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Avg, F, Q
from django.utils import dateparse, timezone
from django.views.generic import DetailView, ListView, TemplateView

from localhost.core.models import (Bid, BiddingSession, Booking, Notification,
                                   Property, PropertyItem, PropertyItemReview)
from localhost.core.utils import parse_address

logger = logging.getLogger(__name__)
User = get_user_model()


class PropertyDetailView(DetailView):
    """
    View that shows property and its property items.
    """
    queryset = Property.objects.prefetch_related('property_item')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        property = self.get_object()
        property_item = property.property_item.all()[0]
        if property_item and property_item.current_session:
            context['session_end'] = property_item.current_session.end_time
        if self.request.user.is_authenticated:
            context['notifications'] = self.request.user.notification_set.all()
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
                Avg('rating'))['rating__avg'] or 0
            property_item.current_session = \
                BiddingSession.current_session_of(property_item)
            try:
                property_item.current_price = \
                    property_item.bids.latest().amount
                property_item.has_bid = True
                property_item.highest_bidder = \
                    property_item.bids.latest().bidder
            except Bid.DoesNotExist:
                property_item.current_price = property_item.min_price
                property_item.has_bid = False
        return property


class SearchResultsView(ListView):
    """
    View that display search results.
    """
    model = Property
    template_name = 'core/search_results.html'
    paginate_by = 18

    def get_queryset(self, **kwargs):
        """
        Parses url parameters and display a list of property as a result,
        sorted by distance, filtered by number of guests, check-in times.
        """
        args = self.request.GET
        logger.debug(args)

        try:
            lat = Decimal(args.get('lat', settings.DEFAULT_SEARCH_COORD[0]))
            lng = Decimal(args.get('lng', settings.DEFAULT_SEARCH_COORD[1]))
        except (ValueError, InvalidOperation):
            address = args.get('addr')
            if address:
                lat, lng = parse_address(address)
            else:
                # address also empty
                lat, lng = parse_address(settings.DEFAULT_SEARCH_ADDRESS)
            lat, lng = Decimal(lat), Decimal(lng)

        guests = int(args.get('guests', 1))
        bid_now = args.get('bidding-active', 'off')
        # default checkin time is set half an hour from now
        default_checkin = (
            timezone.localtime() + timedelta(minutes=30)).strftime('%H:%M')
        checkin = dateparse.parse_time(args.get('checkin', default_checkin))
        lat_offset, lng_offset = Decimal(0.15), Decimal(0.15)
        lat_range = (lat - lat_offset, lat + lat_offset)
        lng_range = (lng - lng_offset, lng + lng_offset)
        properties = Property.objects.within(lat, lng).filter(
            latitude__range=lat_range,
            longitude__range=lng_range,
            property_item__capacity__gte=guests)

        if bid_now == 'on':
            now = timezone.localtime()

            qs1 = PropertyItem.objects.filter(
                Q(session__start_time__lte=F('session__end_time')),
                Q(session__start_time__lte=now),
                session__end_time__gte=now)

            qs2 = PropertyItem.objects.filter(
                Q(session__start_time__gt=F('session__end_time')),
                Q(session__start_time__lte=now)
                | Q(session__end_time__gte=now))

            properties = properties.filter(
                id__in=qs1.union(qs2).filter(available=True) \
                    .values_list('property_id', flat=True).distinct())

        return properties.distinct().order_by('distance')


class ProfileView(DetailView):
    """
    View that display user public profile.
    """
    model = User
    template_name = 'core/public_profile.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        born = self.get_object().dob
        today = timezone.now()
        if born:
            context['age'] = today.year - born.year \
                - ((today.month, today.day) < (born.month, born.day))
        else:
            context['age'] = None
        return context


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['last_booking'] = self.request.user \
                .booking_set \
                .select_related('property_item__property') \
                .latest('earliest_checkin_time')
        except Booking.DoesNotExist:
            context['last_booking'] = None
        except AttributeError:
            # user not logged in
            pass
        return context
