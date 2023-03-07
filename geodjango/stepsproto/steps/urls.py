from django.urls import path

from steps.views import StepsMapView

app_name="steps"

urlpatterns = [
    path("map", StepsMapView.as_view())
]