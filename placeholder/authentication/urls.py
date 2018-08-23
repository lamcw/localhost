from django.urls import path, include

app_name = 'authentication'

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
]
