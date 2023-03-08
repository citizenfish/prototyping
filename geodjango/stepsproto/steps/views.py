import json

from django.core.serializers import serialize
from django.views.generic.base import TemplateView

from siteartifacts.models import IndexPage
from steps.models import Step, Route

class IndexView(TemplateView):
    template_name = 'index.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['index'] = IndexPage.objects.last()
        context['routes'] = Route.objects.all()
        return context

class StepsMapView(TemplateView):
    template_name = "map.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['steps'] = json.loads(serialize("geojson", Step.objects.all()))
        return context

class RoutesView(TemplateView):
    template_name = "route.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(kwargs)
        route = Route.objects.get(pk=kwargs.get('pk'))
        context['route'] = route
        steps = route.steps.all()
        context['geojson'] = json.loads(serialize("geojson", steps, geometry_field='location', fields=('name',)))
        context['steps'] = steps
        return context