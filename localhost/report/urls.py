from django.urls import path

from . import views

app_name = 'report'

urlpatterns = [
    path(
        'user/<int:pk>', views.UserReportCreate.as_view(), name='report-user'),
    path(
        'property-item/<int:pk>',
        views.PropertyItemReportCreate.as_view(),
        name='report-property-item')
]
