import json

from django.core.serializers import serialize
from django.views.generic.base import TemplateView

from steps.models import Step

class StepsMapView(TemplateView):
    template_name = "map.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['steps'] = json.loads(serialize("geojson", Step.objects.all()))
        return context
