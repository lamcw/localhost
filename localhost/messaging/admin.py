from django.contrib import admin

from localhost.messaging.models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    pass
