from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
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
