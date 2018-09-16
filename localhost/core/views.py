from datetime import timedelta

from django.db.models import Case, F, Q, When
from django.utils import dateparse, timezone
from django.views.generic import DetailView, ListView
from geopy import distance

from localhost.core.models import Property, PropertyItem


class PropertyDetailView(DetailView):
    queryset = Property.objects.prefetch_related()


class PropertyItemDetailView(DetailView):
    queryset = PropertyItem.objects.prefetch_related()
    template_name = 'core/property_item_detail.html'
    context_object_name = 'property_item'


class SearchResultsView(ListView):
    model = Property
    template_name = 'core/search_results.html'
    paginate_by = 20

    def get_queryset(self, **kwargs):
        queryset = super(SearchResultsView, self).get_queryset()
        url_params = self.request.GET

        latitude = float(url_params.get('lat', -33.8688))
        longitude = float(url_params.get('lng', 151.2039))
        guests = int(url_params.get('guests', 1))
        bid_now = url_params.get('bidding-active', 'false')
        # default checkin time is set half an hour from now
        default_checkin = (
            timezone.now() + timedelta(minutes=30)).time().strftime('%H:%M')
        checkin = dateparse.parse_time(
            url_params.get('checkin', default_checkin))

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
                property_item__session__end_time__gt=timezone.now().time(),
                property_item__session__start_time__lte=timezone.now().time(),
                property_item__available=True,
                property_item__capacity__gte=guests).distinct()

        properties = list()

        for p in queryset:
            geodesic_distance = distance.distance(
                (latitude, longitude), (p.latitude, p.longitude)).kilometers
            properties.append(tuple((p.id, geodesic_distance)))

        sorted_properties = sorted(properties, key=lambda x: x[1])
        sorted_ids = [i[0] for i in sorted_properties]
        preserved = Case(
            *[When(pk=pk, then=pos) for pos, pk in enumerate(sorted_ids)])

        return queryset.filter(pk__in=sorted_ids).order_by(preserved)
