from django.shortcuts import render

# Create your views here.
from django.utils.safestring import mark_safe
from django.views.generic.base import TemplateView
from mygoals.models import Goal, Event


import plotly
from plotly.graph_objs import Scatter, Layout
import BeautifulSoup
from datetime import date

START_DT, STOP_DT = date(2017, 1, 1), date(2017, 12, 31)


class ContextMixin(object):

    def get_context_data(self, *args, **kwargs):
        context = super(ContextMixin, self).get_context_data(*args, **kwargs)
        goals = Goal.objects.all()
        events = Event.objects.all().order_by('datetime')
        context.update(all_goals=goals, all_events=events)
        return context



class HomeView(ContextMixin, TemplateView):
    template_name = 'mygoals/home.html'


    def get_context_data(self, *args, **kwargs):
        context = super(HomeView, self).get_context_data(*args, **kwargs)

        plotly.tools.set_credentials_file(username='JosPolfliet', api_key='5jv4xPhzAis6ZqiOIA9B')
        #plotly.tools.set_credentials_file(username='nousername123', api_key='lPOTxgmmGo4CGywT2y1K')
        goals = Goal.objects.all()

        context.update(
            goals=goals
        )

        return context
