# from django.apps.config import AppConfig
# from django.conf import settings
# settings.configure()
#
# import django
# django.setup()
#
#
#
# from django.apps import apps
#
# Goal = apps.get_app_config('mygoals').get_model('Goal')
# Event = apps.get_app_config('mygoals').get_model('Event')
from mygoals.models import Goal, Event
from datetime import date, timedelta as td
import random


sport = Goal.objects.get(id=1)
github = Goal.objects.get(id=2)
books= Goal.objects.get(id=4)
alcohol= Goal.objects.get(id=5)
dates = Goal.objects.get(id=3)


startdt = date(2017, 1, 1)
Event.objects.all().delete()

for i in xrange(1,100):
    e = Event(goal=sport, value=1, event_dt=startdt + td(days=i*random.randint(1,4)), notes='Sport {} km'.format(i))
    e.save()
    e = Event(goal=github, value=random.randint(1,5), event_dt=startdt + td(days=random.randint(10,340)), notes='New likes {}'.format(i))
    e.save()
    e = Event(goal=alcohol, value=random.randint(0,8), event_dt=startdt + td(days=i*3), notes='{} duvels gedronken'.format(i))
    e.save()

for i in xrange(1,8):
    e = Event(goal=dates, value=1, event_dt=startdt + td(days=random.randint(10,340)), notes='Zeer plezante date met Victo deel {}'.format(i))
    e.save()
    e = Event(goal=books, value=1, event_dt=startdt + td(days=random.randint(10,340)), notes='Goed book gelezen deel {}'.format(i))
    e.save()

