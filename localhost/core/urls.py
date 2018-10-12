from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path(
        '',
        views.HomeView.as_view(),
        name='home'),
    path(
        'property/<int:pk>',
        views.PropertyDetailView.as_view(),
        name='property-detail'),
    path('search/', views.SearchResultsView.as_view(), name='search-results'),
    path('profile/<int:pk>', views.ProfileView.as_view(), name='profile'),
]
