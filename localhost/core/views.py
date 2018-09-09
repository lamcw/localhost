from django.views.generic import DetailView

from localhost.core.models import Property


class PropertyDetailView(DetailView):
    model = Property
    template_name = 'core/listing_details.html'
