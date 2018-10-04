from django.db.models import Q
from django.views.generic import ListView

from localhost.messaging.models import Message


class MessagingView(ListView):
    template_name = 'messaging/messaging.html'
    model = Message

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recipient'] = self.request.GET.get('recipient')
        conversations = []

        auth_user = self.request.user
        messages = self.model.objects.filter(
            Q(sender=auth_user) | Q(recipient=auth_user))
        contacts = messages.values('sender', 'recipient').distinct() \
            .exclude(sender=auth_user, recipient=auth_user)
        for user in contacts:
            conversation = (user, messages.filter(sender=user, recipient=user))
            conversations.append(conversation)
        context['conversations'] = conversations
        return context
