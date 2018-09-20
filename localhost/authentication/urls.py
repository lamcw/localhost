from django.urls import include, path
from django.views.defaults import page_not_found

from . import views

app_name = 'authentication'

urlpatterns = [
    # override default view
    path('accounts/login/', views.LoginView.as_view(), name='login'),
    # disable default password change view(s)
    path('accounts/password_change/', page_not_found,
         {'exception': Exception()}),
    path('accounts/password_change/done', page_not_found,
         {'exception': Exception()}),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register', views.SignUpView.as_view(), name='register'),
]
