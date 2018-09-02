from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from placeholder.authentication.forms import SignUpForm


class SignUpView(UserPassesTestMixin, FormView):
    template_name = 'registration/signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('core:index')

    def test_func(self):
        return not self.request.user.is_authenticated

    def form_valid(self, form):
        form.save()
        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=raw_password)
        login(self.request, user)
        return super().form_valid(form)


class LoginView(UserPassesTestMixin, LoginView):
    def test_func(self):
        return not self.request.user.is_authenticated
