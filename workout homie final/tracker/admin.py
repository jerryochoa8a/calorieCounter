from django.contrib import admin
from .models import Goal, DailyLog, Workout

admin.site.register(Goal)
admin.site.register(DailyLog)
admin.site.register(Workout)