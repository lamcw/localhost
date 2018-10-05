from django.contrib.auth import get_user_model
from django.db.models import Q
from django.views.generic import ListView

from localhost.messaging.models import Message

User = get_user_model()


class MessagingView(ListView):
    template_name = 'messaging/messaging.html'
    model = Message

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            recipient = User.objects.get(pk=self.request.GET.get('recipient'))
            context['recipient'] = recipient
        except User.DoesNotExist:
            pass

        auth_user = self.request.user
        messages = self.model.objects.filter(
            Q(sender=auth_user) | Q(recipient=auth_user))
        contacts = User.objects \
            .filter(
                Q(sent_messages__pk__in=messages.values('pk'))
                | Q(received_messages__pk__in=messages.values('pk'))) \
            .exclude(pk=auth_user.pk).distinct()
        conversations = [(user,
                          messages.filter(Q(sender=user) | Q(recipient=user)))
                         for user in contacts]
        context['conversations'] = conversations
        return context
