from django.db import models
from chats.models import Chat


class Gym(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, null=True, default=None)


class Training(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    weekday = models.IntegerField()  # 0-6
    sport = models.CharField(max_length=255, blank=True, null=True, default=None)
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE)
    time = models.TimeField()


class TrainingCorrection(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    CORRECTION_TYPE_CHOISES = (
        ('move', "move"),
        ('remove', "remove"),
        ('add', "add"),
    )
    correction_type = models.CharField(max_length=100, choices=CORRECTION_TYPE_CHOISES)

    old_date = models.DateTimeField(null=True)
    old_time = models.TimeField(null=True)
    old_gym = models.ForeignKey(Gym, on_delete=models.CASCADE, null=True, related_name='moved_from')

    new_date = models.DateTimeField(null=True)
    new_time = models.TimeField(null=True)
    new_gym = models.ForeignKey(Gym, on_delete=models.CASCADE, null=True, related_name='moved_in')
    created_at = models.DateTimeField(auto_now_add=True)
