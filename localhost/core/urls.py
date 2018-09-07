from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'core'

urlpatterns = [
    path(
        '',
        TemplateView.as_view(template_name='core/index.html'),
        name='index'),
    path(
        'listing/<int:pk>',
        views.PropertyItemDetailView.as_view(),
        name='listing-details'),
    path('search/', views.SearchResultsView.as_view(), name='search_results'),
]
