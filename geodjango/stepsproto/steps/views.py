import json

from django.core.serializers import serialize
from django.views.generic.base import TemplateView
from django.db.models import F

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
        context['geojson'] = json.loads(serialize("geojson", [step], geometry_field='location', fields=('name','icon',)))
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
        context['steps'] = route.steps.all()
        context['instructions'] = RouteInstruction.objects.filter(route=kwargs.get('pk')).annotate(name=F('locationname'))
        instructions_geojson = json.loads(serialize("geojson", context['instructions'], geometry_field='location', fields=('locationname','icon',)))
        steps_geojson = json.loads(serialize("geojson", context['steps'], geometry_field='location', fields=('name', 'icon',)))

        startpoint_feature = {
            "type": "Feature",
            "geometry": json.loads(route.startpoint.geojson),
            "properties": {
                "name": "Start Point",
                "icon": "start"
            }
        }

        endpoint_feature = {
            "type": "Feature",
            "geometry": json.loads(route.endpoint.geojson),
            "properties": {
                "name": "End Point",
                "icon": "end"
            }
        }

        # Rename the 'locationname' field to 'name' in the GeoJSON
        for feature in instructions_geojson['features']:
            feature['properties']['name'] = feature['properties'].pop('locationname')

        context['geojson'] = {
            "type": "FeatureCollection",
            "features": steps_geojson['features'] + instructions_geojson['features'] + [startpoint_feature] + [endpoint_feature]
        }

        return context