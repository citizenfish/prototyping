import json

from django.core.serializers import serialize
from django.views.generic.base import TemplateView

from siteartifacts.models import IndexPage
from steps.models import Step,StepImage, Route, RouteInstruction

class IndexView(TemplateView):
    template_name = 'index.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['index'] = IndexPage.objects.last()
        context['routes'] = Route.objects.all()
        return context

class StepsMapView(TemplateView):
    template_name = "step.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        step = Step.objects.get(pk=kwargs.get('pk'))
        context['geojson'] = json.loads(serialize("geojson", [step], geometry_field='location', fields=('name',)))
        context['step'] = step

        # Now get related images
        context['stepimages'] = StepImage.objects.filter(step=kwargs.get('pk'))
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
        context['instructions'] = RouteInstruction.objects.filter(route=kwargs.get('pk'))

        return context