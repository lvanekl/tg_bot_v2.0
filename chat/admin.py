from django.contrib import admin
from .models import Chat, ChatAdministrator, ChatSettings


class ChatAdmin(admin.ModelAdmin):
    model = Chat
    list_display = ('id', 'chat_id',)


class ChatSettingsAdmin(admin.ModelAdmin):
    model = ChatSettings

    list_display = ('id', 'chat', 'welcome_meme', 'auto_poll',
                    'GPT_question', 'GPT_yes', 'GPT_maybe', 'GPT_no',
                    'emoji', 'everyone_is_administrator', 'language', 'poll_send_time')


class ChatAdministratorAdmin(admin.ModelAdmin):
    model = ChatAdministrator
    list_display = ('id', 'chat_id', 'user_id')


# Register your models here.
admin.site.register(Chat, ChatAdmin)
admin.site.register(ChatSettings, ChatSettingsAdmin)
admin.site.register(ChatAdministrator, ChatAdministratorAdmin)
