from django.urls import path, reverse_lazy
from django.views.generic import RedirectView, TemplateView

from . import views

app_name = 'dashboard'

urlpatterns = [
    path(
        '',
        RedirectView.as_view(url=reverse_lazy('dashboard:profile')),
        name='dashboard'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('active-bids/', views.ActiveBidsView.as_view(), name='bids'),
    path('listing/add/', views.ListingCreate.as_view(), name='listing-create'),
    path(
        'listing/<int:pk>/',
        views.ListingUpdate.as_view(),
        name='listing-update'),
    path(
        'listing/<int:pk>/delete',
        views.ListingDelete.as_view(),
        name='listing-delete'),
    path(
        'booking-history/',
        views.BookingListView.as_view(),
        name='booking-history'),
    path(
        'review/listing/<int:pk>',
        views.ListingReviewView.as_view(),
        name='listing-review')
]
