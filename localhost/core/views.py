import math

from django.views.generic import DetailView, ListView
from geopy import distance, units

from localhost.core.models import PropertyItem, Property


class PropertyItemDetailView(DetailView):
    model = PropertyItem
    template_name = 'core/listing_details.html'


class SearchResultsView(ListView):
    model = Property
    template_name = 'core/search_results.html'

    def get_queryset(self, **kwargs):
        queryset = super(SearchResultsView, self).get_queryset()

        latitude = -33.96667  #hurstville
        longitude = 151.1
        search_range = 14
        guests = 5

        # "Box" range filter to narrow queries
        latitude_offset = units.degrees(arcminutes=units.nautical(kilometers=search_range))
        longitude_offset = latitude_offset / math.cos(math.radians(latitude))
        queryset = queryset.filter(
            latitude__range = (latitude - latitude_offset, latitude + latitude_offset),
            longitude__range = (longitude - longitude_offset, longitude + longitude_offset)
        )

        properties = []
        for p in queryset:
            # TODO session filter
            geodesic_distance = distance.distance(
                (latitude, longitude), (p.latitude, p.longitude)
            ).kilometers
            if geodesic_distance < search_range:
                property_item_list = PropertyItem.objects.filter(property__id=p.id)
                for property_item in property_item_list:
                    if property_item.available & (property_item.capacity >= guests):
                        properties.append(p)
                        break

        return queryset.filter(id__in=[p.id for p in properties])
