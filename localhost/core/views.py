from datetime import date, datetime, time, timedelta

from django.db.models import Case, F, Q, When
from django.views.generic import DetailView, ListView
from geopy import distance

from localhost.core.models import Property, PropertyItem, Bid


class PropertyDetailView(DetailView):
    queryset = Property.objects.prefetch_related()


class PropertyItemDetailView(DetailView):
    queryset = PropertyItem.objects.prefetch_related()
    template_name = 'core/property_item_detail.html'
    context_object_name = 'property_item'

    def get_context_data(self, **kwargs):
        context = super(PropertyItemDetailView, self).get_context_data(**kwargs)
        if Bid.objects.filter(property_item=self.kwargs.get('pk')).exists():
            context['current_price'] = Bid.objects.filter(
                property_item=self.kwargs.get('pk')).latest('bid_amount').bid_amount
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
        queryset = super(SearchResultsView, self).get_queryset()
        url_parameters = self.request.GET

        time_now = time(21, 0)
        latitude = float(url_parameters.get('lat', -33.8688))
        longitude = float(url_parameters.get('lng', 151.2039))
        guests = int(url_parameters.get('guests', 1))
        bid_now = url_parameters.get('bidding-active', 'off')
        # default checkin time is set half an hour from now
        default_checkin = (datetime.combine(date.today(), time_now) +
                           timedelta(minutes=30)).strftime('%H%M')
        checkin = datetime.strptime(
            url_parameters.get('checkin', default_checkin), "%H%M").time()

        if bid_now == 'on':
            # filter if checkin times are on same day
            q1 = queryset.filter(
                Q(earliest_checkin_time__lt=F('latest_checkin_time')),
                Q(earliest_checkin_time__lte=checkin),
                latest_checkin_time__gt=checkin)
            # filter if checkin times cross midnight
            q2 = queryset.filter(
                Q(earliest_checkin_time__gt=F('latest_checkin_time')),
                Q(earliest_checkin_time__lte=checkin)
                | Q(latest_checkin_time__gt=checkin))

            queryset = q1 | q2

            queryset = queryset.filter(
                property_item__session__end_time__gt=time_now,
                property_item__session__start_time__lte=time_now,
                property_item__available=True,
                property_item__capacity__gte=guests).distinct()

        properties = list()

        for p in queryset:
            geodesic_distance = distance.distance(
                (latitude, longitude), (p.latitude, p.longitude)).kilometers
            properties.append(tuple((p.id, geodesic_distance)))

        sorted_properties = sorted(properties, key=lambda x: x[1])
        sorted_ids = list(i[0] for i in sorted_properties)
        preserved = Case(
            *[When(pk=pk, then=pos) for pos, pk in enumerate(sorted_ids)])

        return queryset.filter(pk__in=sorted_ids).order_by(preserved)
