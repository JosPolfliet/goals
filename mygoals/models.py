from __future__ import unicode_literals

import datetime

import django
from django.db import models

import plotly
from django.db.models.aggregates import Max
from django.utils.safestring import mark_safe
from plotly.graph_objs import Scatter, Layout
from django.utils.timezone import localtime, make_aware

import BeautifulSoup
from datetime import date

START_DT, STOP_DT =  make_aware(datetime.datetime(2017, 1, 1, 0, 0, 0)), make_aware(datetime.datetime(2017, 12, 31, 23, 59, 59))


class Goal(models.Model):
    name = models.CharField(max_length=100)
    target = models.IntegerField()
    begin_value = models.IntegerField(default=0)
    description = models.TextField(blank=True)

    last_plot_dt = models.DateTimeField(default=django.utils.timezone.now)
    plotly_url = models.CharField(max_length=100)

    def __str__(self):
        return '%s (%s)' % (self.name, self.target)

    def _refresh_plot(self):
        events=Event.objects.filter(goal=self).order_by('event_dt')
        print self

        if len(events) == 0:
            return

        dates = [START_DT]
        values = [self.begin_value]
        notes = ["New Year"]

        for e in events:
            dates.append(e.event_dt)
            values.append(values[-1]+float(e.value))
            notes.append(" new value {}\n Notes: {}".format(e.value, e.notes))

        days_elapsed = (dates[-1]-START_DT).days
        days_elapsed_at_end = (STOP_DT-START_DT).days
        prop_dates_passed = min(days_elapsed*1.0/days_elapsed_at_end,1)

        gap_beginning = self.target-self.begin_value
        gap_expected = gap_beginning * prop_dates_passed
        gap_now = values[-1]-self.begin_value

        progress = gap_now / gap_expected

        red = min(int(-230/(1.3-1)*(progress-1.3)),255)
        green = min(int(230/(1-0.7)*(progress-0.7)),255)

        plot = plotly.plotly.plot({
            "data": [Scatter(x=dates, y=values, name='{}% on track'.format(int(progress*100)), text=notes, marker=dict(color="rgb({},{},0)".format(red, green))),
                     Scatter(x=[START_DT, STOP_DT], y=[self.begin_value, self.target], name='Target',  marker=dict(color="lightgrey")
                             )],
            "layout": Layout(title=self.name,
                             xaxis=dict(
                                range=[START_DT, STOP_DT],
                                nticks=13,
                            ),
                            yaxis=dict(
                                range=[self.begin_value, self.target],

                            ),
                            margin=plotly.graph_objs.Margin(
                                 l=50,
                                 r=25,
                                 b=80,
                                 t=25,
                                pad=10
                            ),
                            showlegend=False,
                            hovermode='text'
                        ),

        }, auto_open=False, displayModeBar = False, showLink=False, link=False)

        self.plotly_url = plot
        self.last_plot_dt = django.utils.timezone.now()
        self.save()

    def _update_if_necessary(self):
        last_event_dt = Event.objects.filter(goal=self).aggregate(Max('load_dt'))[u'load_dt__max']
        if last_event_dt is None or localtime(last_event_dt) > localtime(self.last_plot_dt):
            self._refresh_plot()

    @property
    def plot_link(self):
        self._update_if_necessary()
        return self.plotly_url

class Event(models.Model):
    goal = models.ForeignKey(Goal)
    event_dt = models.DateTimeField(default=django.utils.timezone.now)
    value = models.DecimalField(default=1, decimal_places=2, max_digits=20)
    notes = models.TextField(blank=True)
    url = models.URLField(blank=True)
    load_dt = models.DateTimeField(default=django.utils.timezone.now)

    def __str__(self):
        return '%s: %s - (%s)' % (self.event_dt, self.goal.name, self.value)

