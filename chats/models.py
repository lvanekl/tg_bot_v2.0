from django.db import models
from env.default_chat_settings import *


# Create your models here.
class Chat(models.Model):
    chat_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class ChatSettings(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)

    welcome_meme = models.ImageField(default=DEFAULT_WELCOME_MEME_PATH)

    auto_poll = models.BooleanField(default=DEFAULT_AUTO_POLL_FLAG)
    GPT_question = models.BooleanField(default=DEFAULT_GPT_QUESTION)
    GPT_yes = models.BooleanField(default=DEFAULT_GPT_YES)
    GPT_maybe = models.BooleanField(default=DEFAULT_GPT_MAYBE)
    GPT_no = models.BooleanField(default=DEFAULT_GPT_NO)
    emoji = models.BooleanField(default=DEFAULT_CHAT_EMOJI_FLAG)

    everyone_is_administrator = models.BooleanField(default=DEFAULT_EVERYONE_IS_ADMIN)

    language = models.CharField(max_length=50, default=DEFAULT_LANGUAGE)

    poll_send_time = models.TimeField(default=DEFAULT_POLL_SEND_TIME)


class ChatAdministrator(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user_id = models.IntegerField()
