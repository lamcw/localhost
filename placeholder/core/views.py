from django.shortcuts import render
from django.views.generic import DetailView
from django.conf import settings

from placeholder.core.models import Property


def index(request):
    return render(request, 'core/index.html')


def property_details(request, pk):
    p = Property.objects.get(pk=pk)
    context = {'property': p}
    return render(request, 'core/property_details.html', context)
