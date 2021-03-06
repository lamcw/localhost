from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path(
        'property/<int:pk>',
        views.PropertyDetailView.as_view(),
        name='property-detail'),
    path('search/', views.SearchResultsView.as_view(), name='search-results'),
    path('profile/<int:pk>', views.ProfileView.as_view(), name='profile'),
    path(
        'about',
        TemplateView.as_view(template_name='core/about_us.html'),
        name='about'),
]

handler404 = 'core.views.PageNotFoundView'
