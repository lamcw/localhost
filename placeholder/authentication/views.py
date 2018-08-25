from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render

from placeholder.authentication.forms import SignUpForm


def logged_in_check(user):
    return not user.is_authenticated


@user_passes_test(
    logged_in_check, login_url='core:index', redirect_field_name=None)
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('core:index')
    else:
        form = SignUpForm()
    context = {'form': form}
    return render(request, 'registration/signup.html', context)
