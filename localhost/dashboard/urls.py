from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from django.views.generic import RedirectView

from . import views

app_name = 'dashboard'

urlpatterns = [
    path(
        '',
        RedirectView.as_view(url=reverse_lazy('dashboard:profile')),
        name='dashboard'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('active-bids/', views.ActiveBidsView.as_view(), name='bids'),
    path('listing/', views.ListingListView.as_view(), name='listing-list'),
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
        name='listing-review'),
    path(
        'password-change',
        auth_views.PasswordChangeView.as_view(
            template_name='dashboard/settings.html',
            success_url=reverse_lazy('password-change-done')),
        name='password-change'),
    path(
        'password-change/done',
        auth_views.PasswordChangeDoneView.as_view(),
        name='password-change-done')
]
