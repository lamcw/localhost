from datetime import datetime, time, timedelta

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import (BooleanField, Case, Exists, F, Max, OuterRef,
                              Subquery, Value, When)
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, UpdateView
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from django.views.generic.edit import ProcessFormView

from localhost.core.models import (Bid, Booking, Property, PropertyImage,
                                   PropertyItem, PropertyItemImage,
                                   PropertyItemReview)
from localhost.dashboard.forms import (ProfileForm, PropertyForm,
                                       PropertyItemFormSet, WalletForm)


class MultiFormMixin(ContextMixin):
    """
    View mixin to process multiple forms in one view.

    See:
        https://gist.github.com/jamesbrobb/748c47f46b9bd224b07f
    """
    form_classes = {}
    prefixes = {}
    success_urls = {}
    grouped_forms = {}

    initial = {}
    prefix = None
    success_url = None

    def get_form_classes(self):
        return self.form_classes

    def get_forms(self, form_classes, form_names=None, bind_all=False):
        """
        Instantiate all forms in view.

        Args:
            form_classes: a dict of form classes
            form_names: list of form names
            bind_all: True if instantiate forms with POST or PUT

        Return:
            dict containing form instances
        """
        return dict([(key,
                      self._create_form(key, klass,
                                        (form_names and key in form_names)
                                        or bind_all))
                     for key, klass in form_classes.items()])

    def get_form_kwargs(self, form_name, bind_form=False):
        """
        Generate form kwargs.

        Args:
            form_name: name of form
            bind_form: True if instantiate form with POST or PUT

        Return:
            dict containing form init kwargs
        """
        kwargs = {}
        kwargs.update({'initial': self.get_initial(form_name)})
        kwargs.update({'prefix': self.get_prefix(form_name)})

        if bind_form:
            kwargs.update(self._bind_form_data())

        return kwargs

    def forms_valid(self, forms, form_name):
        """
        Call form_valid() in a form.

        Args:
            forms: dict of forms containing form to be validated, with
                form_name as key of the form
            form_name: name of form. This method looks for
                [form_name]_form_valid in subclass and call it. If method is
                not found, it redirects to success_url of form_name

        Return:
            either return value of [form_name]_form_valid() or redirects to
            success_url of form_name
        """
        form_valid_method = '%s_form_valid' % form_name
        if hasattr(self, form_valid_method):
            return getattr(self, form_valid_method)(forms[form_name])
        else:
            return redirect(self.get_success_url(form_name))

    def forms_invalid(self, forms):
        """
        Renders to form invalid.
        """
        return self.render_to_response(self.get_context_data(forms=forms))

    def get_initial(self, form_name):
        """
        Get initial data of form_name.

        Args:
            form_name: name of form to get initial data from

        Return:
            initial data
        """
        initial_method = 'get_%s_initial' % form_name
        if hasattr(self, initial_method):
            return getattr(self, initial_method)()
        else:
            return self.initial.copy()

    def get_prefix(self, form_name):
        """
        Get prefix of form.

        Args:
            form_name: name of form

        Return:
            prefix of form
        """
        return self.prefixes.get(form_name, self.prefix)

    def get_success_url(self, form_name=None):
        """
        Get success url of form.

        Args:
            form_name: name of form

        Return:
            success url of form_name
        """
        return self.success_urls.get(form_name, self.success_url)

    def _create_form(self, form_name, klass, bind_form):
        """
        Instantiate form given form class and form name

        Args:
            form_name: name of form
            klass: class (not instance) of form
            bind_form: True if bind form with data

        Return:
            new form instance
        """
        form_kwargs = self.get_form_kwargs(form_name, bind_form)
        form_create_method = 'create_%s_form' % form_name
        if hasattr(self, form_create_method):
            form = getattr(self, form_create_method)(**form_kwargs)
        else:
            form = klass(**form_kwargs)
        return form

    def _bind_form_data(self):
        """
        Bind data to form.
        """
        if self.request.method in ('POST', 'PUT'):
            return {
                'data': self.request.POST,
                'files': self.request.FILES,
            }
        return {}


class ProcessMultipleFormsView(ProcessFormView):
    """
    View that can process multiple forms.
    """

    def get(self, request, *args, **kwargs):
        """
        Generate forms and chuck them in context.
        """
        form_classes = self.get_form_classes()
        forms = self.get_forms(form_classes)
        return self.render_to_response(self.get_context_data(forms=forms))

    def post(self, request, *args, **kwargs):
        """
        Process forms from POST request data.
        """
        form_classes = self.get_form_classes()
        # form submite button must have name="action"
        form_name = request.POST.get('action')
        if self._individual_exists(form_name):
            return self._process_individual_form(form_name, form_classes)
        elif self._group_exists(form_name):
            return self._process_grouped_forms(form_name, form_classes)
        else:
            return self._process_all_forms(form_classes)

    def _individual_exists(self, form_name):
        return form_name in self.form_classes

    def _group_exists(self, group_name):
        return group_name in self.grouped_forms

    def _process_individual_form(self, form_name, form_classes):
        forms = self.get_forms(form_classes, (form_name, ))
        form = forms.get(form_name)
        if not form:
            return HttpResponseForbidden()
        elif form.is_valid():
            return self.forms_valid(forms, form_name)
        else:
            return self.forms_invalid(forms)

    def _process_grouped_forms(self, group_name, form_classes):
        form_names = self.grouped_forms[group_name]
        forms = self.get_forms(form_classes, form_names)
        if all([
                forms.get(form_name).is_valid()
                for form_name in form_names.values()
        ]):
            return self.forms_valid(forms)
        else:
            return self.forms_invalid(forms)

    def _process_all_forms(self, form_classes):
        forms = self.get_forms(form_classes, None, True)
        if all([form.is_valid() for form in forms.values()]):
            return self.forms_valid(forms)
        else:
            return self.forms_invalid(forms)


class BaseMultipleFormsView(MultiFormMixin, ProcessMultipleFormsView):
    """
    A base view for displaying several forms.
    """
    pass


class MultiFormsView(TemplateResponseMixin, BaseMultipleFormsView):
    """
    A view for displaying several forms, and rendering a template response.
    """
    pass


class DashboardView(LoginRequiredMixin, MultiFormsView):
    template_name = 'dashboard/dashboard_base.html'
    form_classes = {
        'wallet': WalletForm,
        'profile': ProfileForm,
        'password_change': PasswordChangeForm
    }
    success_url = reverse_lazy('dashboard:dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_bid = Bid.objects.filter(
            property_item=OuterRef('pk'),
            bidder=self.request.user).order_by('-amount')
        context['active_bids'] = PropertyItem.objects \
            .annotate(current_bid=Max('bids__amount')) \
            .filter(bids__bidder=self.request.user).distinct() \
            .annotate(user_bid=Subquery(user_bid.values('amount')[:1]))

        reviews = PropertyItemReview.objects.filter(
            booking=OuterRef('pk'), booking__user=self.request.user)
        # today >= booking.latest_checkin_time.date + 1 day
        # so latest_checkin_time <= today - 1 day
        one_day_ago = timezone.now() - timedelta(days=1)
        context['booking_list'] = Booking.objects.prefetch_related() \
            .filter(user=self.request.user) \
            .order_by('-earliest_checkin_time') \
            .annotate(reviewed=Exists(reviews)) \
            .annotate(passed_one_day=Case(
                When(latest_checkin_time__lte=one_day_ago, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )) \
            .annotate(can_cancel=Case(
                When(
                    earliest_checkin_time__gt=timezone.now(),
                    then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            ))
        context['guest_booking_list'] = Booking.objects.prefetch_related() \
            .filter(property_item__property__host=self.request.user) \
            .order_by('-earliest_checkin_time')
        return context

    def profile_form_valid(self, form):
        form.save(self.request)
        return redirect('dashboard:dashboard')

    def create_profile_form(self, **kwargs):
        return ProfileForm(instance=self.request.user, **kwargs)

    def create_password_change_form(self, **kwargs):
        return PasswordChangeForm(user=self.request.user, **kwargs)

    def password_change_form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        return redirect('dashboard:dashboard')

    def wallet_form_valid(self, form):
        recharge = form.cleaned_data.get('recharge_amount')
        self.request.user.credits = F('credits') + recharge
        self.request.user.save()
        return redirect('dashboard:dashboard')


class PropertyItemReviewMixin(AccessMixin):
    """
    Allow access only if property item review does not exists,
    and the date today is the day after booking.

    URL has to contain <int:pk>
    """
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        try:
            PropertyItemReview.objects.get(booking=kwargs.get('pk'))
            return self.handle_no_permission()
        except ObjectDoesNotExist:
            booking = Booking.objects.get(pk=kwargs.get('pk'))
            # next day after the booking
            date_at_least = datetime.combine(
                booking.latest_checkin_time,
                time(tzinfo=timezone.get_current_timezone())) + timedelta(
                    days=1)
            if timezone.now() >= date_at_least:
                return super().dispatch(request, *args, **kwargs)
            else:
                return self.handle_no_permission()


class ListingCreate(LoginRequiredMixin, CreateView):
    """
    CreateView that combines both ModelForm and InlineModelFormSet.
    """
    model = Property
    form_class = PropertyForm
    template_name = 'dashboard/listing/listing_create.html'
    success_url = reverse_lazy('dashboard:dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # add formset to context
        context['property_item_formset'] = PropertyItemFormSet(
            self.request.POST or None, self.request.FILES or None)
        return context

    def form_valid(self, form):
        """
        Overrides default form_valid to save form and formset.
        """
        context = self.get_context_data()
        property_item_formset = context.get('property_item_formset')
        if form.is_valid() and property_item_formset.is_valid():
            form.instance.host = self.request.user
            self.object = form.save()
            for img in self.request.FILES.getlist('img'):
                PropertyImage.objects.create(property=self.object, img=img)
            for form in property_item_formset:
                property_item = form.save(commit=False)
                property_item.property = self.object
                property_item.save()
                form.save_m2m()
                for img in self.request.FILES.getlist(form.prefix + '-img'):
                    PropertyItemImage.objects.create(
                        property_item=property_item, img=img)
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class ListingUpdate(LoginRequiredMixin, UpdateView):
    model = Property
    form_class = PropertyForm
    success_url = reverse_lazy('dashboard:dashboard')


class ListingDelete(LoginRequiredMixin, DeleteView):
    success_url = reverse_lazy('dashboard:dashboard')


class ListingReviewView(LoginRequiredMixin, PropertyItemReviewMixin,
                        CreateView):
    model = PropertyItemReview
    success_url = reverse_lazy('dashboard:dashboard')
    fields = (
        'rating',
        'description',
    )
    template_name = 'dashboard/property_item_review.html'

    def form_valid(self, form):
        form.instance.booking = Booking.objects.get(id=self.kwargs.get('pk'))
        return super().form_valid(form)
