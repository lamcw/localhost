from django.urls import path
from . import views


app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.SearchResultsView.as_view(), name='search_results'),
    path('property/<int:pk>', views.property_details, name='property_details')
]
