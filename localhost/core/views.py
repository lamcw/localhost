import math

from django.db.models import F, Q, Case, When
from django.views.generic import DetailView, ListView
from geopy import distance, units

from localhost.core.models import Property


class PropertyDetailView(DetailView):
    queryset = Property.objects.select_related()


class SearchResultsView(ListView):
    model = Property
    template_name = 'core/search_results.html'
    paginate_by = 20

    def get_queryset(self, **kwargs):
        queryset = super(SearchResultsView, self).get_queryset()

        # time = datetime.datetime.now()
        time = '14:00:00'
        latitude = float(self.request.GET.get('lat',-33.9666))
        longitude = float(self.request.GET.get('long',151.1))
        guests = int(self.request.GET.get('guests', 1))
        bid_now = int(self.request.GET.get('bidnow', 0))
        checkin = self.request.GET.get('checkin', time)

        if bid_now:
            q1 = queryset.filter(
                Q(earliest_checkin_time__lt=F('latest_checkin_time')),
                Q(earliest_checkin_time__lt=checkin),
                latest_checkin_time__gt=checkin
            )

            q2 = queryset.filter(
                Q(earliest_checkin_time__gt=F('latest_checkin_time')),
                Q(earliest_checkin_time__lt=checkin)
                | Q(latest_checkin_time__gt=checkin)
            )

            queryset = q1 | q2

            queryset = queryset.filter(
                session__end_time__gt=time,
                session__start_time__lt=time,
                property_item__available=True,
                property_item__capacity__gte=guests
            ).distinct()

        properties = list()
        for p in queryset:
            geodesic_distance = distance.distance(
                (latitude, longitude), (p.latitude, p.longitude)).kilometers
            properties.append(tuple((p.id, geodesic_distance)))

        sorted_properties = sorted(properties, key=lambda x: x[1])
        sorted_ids = list(i[0] for i in sorted_properties)
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(sorted_ids)])

        return queryset.filter(pk__in=sorted_ids).order_by(preserved)
