from django.views.generic import DetailView

from placeholder.core.models import PropertyItem


class PropertyItemDetail(DetailView):
    model = PropertyItem
    template_name = 'core/listing_details.html'
