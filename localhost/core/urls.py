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
        'property/<int:pk>',
        views.PropertyDetailView.as_view(),
        name='property-detail'),
    path(
        'property-item/<int:pk>',
        views.PropertyItemDetailView.as_view(),
        name='property-item-detail'),
    path('search/', views.SearchResultsView.as_view(), name='search_results'),
    path('profile/<int:pk>', views.ProfileView.as_view(), name='profile')
]
