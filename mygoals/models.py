from __future__ import unicode_literals

import datetime

import django
from django.db import models

from django.db.models.aggregates import Max
from django.utils.safestring import mark_safe
from django.utils.timezone import localtime, make_aware

import plotly.offline as opy
import plotly.graph_objs as go

START_DT, STOP_DT =  make_aware(datetime.datetime(2018, 1, 1, 0, 0, 0)), make_aware(datetime.datetime(2019, 12, 31, 23, 59, 59))


class Goal(models.Model):
    name = models.CharField(max_length=100)
    target = models.IntegerField()
    begin_value = models.IntegerField(default=0)
    description = models.TextField(blank=True)

    def __str__(self):
        return '%s (%s)' % (self.name, self.target)

    def _get_plot_html(self):
        events=Event.objects.filter(goal=self).order_by('event_dt')
        # print self

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

        red = max(0, min(int(-230/(1.3-1)*(progress-1.3)),255))
        green = max(0, min(int(230/(1-0.7)*(progress-0.7)),255))


        data = [go.Scatter(x=dates, y=values, name='{}% on track'.format(int(progress*100)), text=notes, marker=dict(color="rgb({},{},0)".format(red, green))),
                     go.Scatter(x=[START_DT, STOP_DT], y=[self.begin_value, self.target], name='Target',  marker=dict(color="lightgrey")
                             )]

        layout = self.layout

        figure = go.Figure(data=data, layout=layout)
        return opy.plot(figure, auto_open=False, output_type='div', show_link=False)

    @property
    def graph_html(self):
        return self._get_plot_html()

    @property
    def layout(self):
        return dict(title=self.name,
                  xaxis=dict(
                      range=[START_DT, STOP_DT],
                      nticks=13,
                  ),
                  yaxis=dict(
                      range=[self.begin_value, self.target],

                  ),
                  margin=go.layout.Margin(
                      l=50,
                      r=25,
                      b=80,
                      t=25,
                      pad=10
                  ),
                  showlegend=False,
                  # hovermode='text'
                  )



class Event(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE)
    event_dt = models.DateTimeField(default=django.utils.timezone.now)
    value = models.DecimalField(default=1, decimal_places=2, max_digits=20)
    notes = models.TextField(blank=True)
    url = models.URLField(blank=True)
    load_dt = models.DateTimeField(default=django.utils.timezone.now)

    def __str__(self):
        return '%s: %s - (%s)' % (self.event_dt, self.goal.name, self.value)

