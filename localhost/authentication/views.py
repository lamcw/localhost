from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from localhost.authentication.forms import SignUpForm


class SignUpView(UserPassesTestMixin, FormView):
    """
    Provides sign up view for user. Logs user in if registration is successful.
    """
    template_name = 'registration/register.html'
    form_class = SignUpForm
    success_url = reverse_lazy('core:index')

    def test_func(self):
        return not self.request.user.is_authenticated

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get('email')
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(self.request, email=email, password=raw_password)
        if user is None:
            # error has occured, though this should not happen
            return self.render_to_response(self.get_context_data(form=form))
        login(self.request, user)
        return super().form_valid(form)


class LoginView(UserPassesTestMixin, LoginView):
    def test_func(self):
        """
        User cannot access this page if he/she is authenticated.
        """
        return not self.request.user.is_authenticated
