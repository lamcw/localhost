from django.urls import path

from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.MessagingView.as_view(), name='messages'),

]
