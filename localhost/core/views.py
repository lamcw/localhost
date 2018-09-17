from datetime import timedelta

from django.conf import settings
from django.db.models import F, Q
from django.utils import dateparse, timezone
from django.views.generic import DetailView, ListView

from localhost.core.models import Bid, Property, PropertyItem
from localhost.core.utils import parse_address


class PropertyDetailView(DetailView):
    queryset = Property.objects.prefetch_related()


class PropertyItemDetailView(DetailView):
    queryset = PropertyItem.objects.prefetch_related()
    template_name = 'core/property_item_detail.html'
    context_object_name = 'property_item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if Bid.objects.filter(property_item=self.kwargs.get('pk')).exists():
            context['current_price'] = Bid.objects.filter(
                property_item=self.kwargs.get('pk')).latest(
                    'bid_amount').bid_amount
            context['next_bid'] = context['current_price'] + 5
        else:
            context['current_price'] = PropertyItem.objects.get(
                pk=self.kwargs.get('pk')).min_price
            context['next_bid'] = context['current_price']
        return context


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
            latitude, longitude = parse_address(args.get('address'))

        guests = int(args.get('guests', 1))
        bid_now = args.get('bidding-active', 'off')
        # default checkin time is set half an hour from now
        default_checkin = (
            timezone.now() + timedelta(minutes=30)).strftime('%H:%M')
        checkin = dateparse.parse_time(args.get('checkin', default_checkin))

        properties = self.model.objects.within(latitude, longitude)

        if bid_now == 'on':
            # filter if checkin times are on same day
            q1 = properties.filter(
                Q(earliest_checkin_time__lt=F('latest_checkin_time')),
                Q(earliest_checkin_time__lte=checkin),
                latest_checkin_time__gt=checkin)
            # filter if checkin times cross midnight
            q2 = properties.filter(
                Q(earliest_checkin_time__gt=F('latest_checkin_time')),
                Q(earliest_checkin_time__lte=checkin)
                | Q(latest_checkin_time__gt=checkin))

            properties = (q1 | q2).filter(
                property_item__session__end_time__gt=timezone.now().time(),
                property_item__session__start_time__lte=timezone.now().time(),
                property_item__available=True,
                property_item__capacity__gte=guests).distinct()

        return properties.order_by('distance')
