from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from localhost.core.models import Property
from localhost.dashboard.forms import (PropertyForm,
                                         PropertyItemImageFormSet, RoomFormSet)


@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    pass


@method_decorator(login_required, name='dispatch')
class ListingCreate(CreateView):
    model = Property
    form_class = PropertyForm
    template_name = 'dashboard/listing/listing_create.html'
    success_url = reverse_lazy('dashboard:dashboard')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['room_formset'] = RoomFormSet(self.request.POST)
            context['image_formset'] = PropertyItemImageFormSet(
                self.request.POST)
        else:
            context['room_formset'] = RoomFormSet()
            context['image_formset'] = PropertyItemImageFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        room_formset = context.get('room_formset')
        property_image_formset = context.get('image_formset')
        if all([
                form.is_valid(),
                room_formset.is_valid(),
                property_image_formset.is_valid()
        ]):
            form.instance.host = self.request.user
            self.object = form.save()
            # save images for property
            for form in property_image_formset:
                image = form.save(commit=False)
                image.property_item = self.object
                form.save()
            # save rooms for property
            for room_form in room_formset:
                r = room_form.save(commit=False)
                r.property_ptr = self.object
                room = room_form.save()
                room_form.save_m2m()
                # save beds and images for each room
                for image_form in room_form.image_formset:
                    image = image_form.save(commit=False)
                    image.property_item = room
                    image_form.save()
                for bed_form in room_form.nested:
                    b = bed_form.save(commit=False)
                    b.room_ptr = room
                    bed = bed_form.save()
                    bed_form.save_m2m()
                    # save images for bed only
                    for image_form in bed_form.image_formset:
                        image = image_form.save(commit=False)
                        image.property_item = bed
                        image_form.save()
            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data(form=form))


@method_decorator(login_required, name='dispatch')
class ListingUpdate(UpdateView):
    model = Property
    form_class = PropertyForm


@method_decorator(login_required, name='dispatch')
class ListingDelete(DeleteView):
    success_url = reverse_lazy('dashboard:dashboard')
