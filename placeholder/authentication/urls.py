from django.urls import include, path

from . import views

app_name = 'authentication'

urlpatterns = [
    # override default view
    path('accounts/login/', views.LoginView.as_view(), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup', views.SignUpView.as_view(), name='signup'),
]
