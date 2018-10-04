from django.db.models import Q
from django.views.generic import ListView

from localhost.messaging.models import Message


class MessagingView(ListView):
    template_name = 'messaging/messaging.html'
    model = Message

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recipient'] = self.request.GET.get('recipient')
        contact_list = []
        conversations = []

        queryset = Message.objects.filter(
            Q(sender=self.request.user) | Q(recipient=self.request.user))
        for message in queryset:
            if (message.sender != self.request.user
                    and message.sender not in contact_list):
                contact_list.append(message.sender)
            elif (message.recipient != self.request.user
                  and message.recipient not in contact_list):
                contact_list.append(message.recipient)
        for user in contact_list:
            conversation = (user, [
                m for m in queryset if m.sender == user or m.recipient == user
            ])
            conversations.append(conversation)
        context['conversations'] = conversations
        return context
