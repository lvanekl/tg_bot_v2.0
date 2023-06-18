from django.contrib import admin
from .models import Gym, ScheduleLine, ScheduleCorrection


class GymAdmin(admin.ModelAdmin):
    model = Gym
    list_display = ('id', 'chat', 'name', 'address')


class ScheduleLineAdmin(admin.ModelAdmin):
    model = ScheduleLine
    list_display = ('id', 'chat', 'weekday', 'sport', 'gym', 'time')


class ScheduleCorrectionAdmin(admin.ModelAdmin):
    model = ScheduleCorrection
    list_display = ('id', 'chat', 'correction_type',
                    'old_date', 'old_time', 'old_gym',
                    'new_date', 'new_time', 'new_gym',
                    'created_at')


# Register your models here.
admin.site.register(Gym, GymAdmin)
admin.site.register(ScheduleLine, ScheduleLineAdmin)
admin.site.register(ScheduleCorrection, ScheduleCorrectionAdmin)
