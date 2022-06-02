# Create your views here.
from django.db.models.functions import Upper
from django.shortcuts import render
from django.views.generic import DetailView, ListView

from ifbcat_api import models


def index(request):
    context = dict()
    return render(
        request=request,
        template_name='ifbcat_api/index.html',
        context=context,
    )


class TeamListView(ListView):
    model = models.Team

    def get_queryset(self):
        return super().get_queryset().order_by(Upper('name'))


class TeamDetailView(DetailView):
    slug_field = 'name'
    model = models.Team


class EventListView(ListView):
    model = models.Event

    def get_queryset(self):
        return super().get_queryset().order_by('-start_date')


class EventDetailView(DetailView):
    model = models.Event


class TrainingListView(ListView):
    model = models.Training

    def get_queryset(self):
        return super().get_queryset().order_by(Upper('name'))


class TrainingDetailView(DetailView):
    model = models.Training
