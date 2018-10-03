from django.shortcuts import render
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
        message_list = []
        queryset = Message.objects.filter(
            Q(sender=self.request.user.id) | Q(recipient=self.request.user.id))
        for message in queryset.reverse():
            if (message.sender != self.request.user
                    and message.sender not in contact_list):
                contact_list.append(message.sender)
            elif (message.recipient != self.request.user
                  and message.recipient not in contact_list):
                contact_list.append(message.recipient)
        for user in contact_list:
            conversation = []
            for message in queryset:
                if message.sender == user or message.recipient == user:
                    conversation.append(message)
            message_list.append(conversation)
        context['contact_list'] = contact_list
        context['message_list'] = message_list
        return context
