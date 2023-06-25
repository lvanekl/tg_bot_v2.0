from django.contrib import admin
from .models import Gym, Training, TrainingCorrection


class GymAdmin(admin.ModelAdmin):
    model = Gym
    list_display = ('id', 'chat', 'name', 'address')


class TrainingAdmin(admin.ModelAdmin):
    model = Training
    list_display = ('id', 'chat', 'weekday', 'sport', 'gym', 'time')


class TrainingCorrectionAdmin(admin.ModelAdmin):
    model = TrainingCorrection
    list_display = ('id', 'chat', 'correction_type',
                    'old_date', 'old_time', 'old_gym',
                    'new_date', 'new_time', 'new_gym',
                    'created_at')


# Register your models here.
admin.site.register(Gym, GymAdmin)
admin.site.register(Training, TrainingAdmin)
admin.site.register(TrainingCorrection, TrainingCorrectionAdmin)
