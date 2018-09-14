from datetime import date, datetime, time, timedelta

from django.db.models import Case, F, Q, When
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormMixin
from geopy import distance

from localhost.core.models import Property


class PropertyDetailView(DetailView):
    queryset = Property.objects.prefetch_related()


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
        bid_now = url_parameters.get('bidding-active', 'false')
        # default checkin time is set half an hour from now
        default_checkin = (datetime.combine(date.today(), time_now) +
                           timedelta(minutes=30)).strftime('%H%M')
        checkin = datetime.strptime(
            self.request.GET.get('checkin', default_checkin), "%H%M").time()

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


class FormListView(FormMixin, ListView):
    def get(self, request, *args, **kwargs):
        # From ProcessFormMixin
        form_class = self.get_form_class()
        self.form = self.get_form(form_class)

        # From BaseListView
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()
        if not allow_empty and len(self.object_list) == 0:
            raise Http404(
                _(u"Empty list and '%(class_name)s.allow_empty' is False.") %
                {'class_name': self.__class__.__name__})

        context = self.get_context_data(
            object_list=self.object_list, form=self.form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
