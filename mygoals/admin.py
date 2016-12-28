from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Event, Goal


class EventInline(admin.StackedInline):
    model = Event
    can_delete = True


class GoalAdmin(ModelAdmin):
    inlines = (EventInline, )

admin.site.register(Event)
admin.site.register(Goal)

