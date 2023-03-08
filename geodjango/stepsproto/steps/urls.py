from django.urls import path

from steps.views import StepsMapView, IndexView, RoutesView

app_name="steps"

urlpatterns = [
    path('', IndexView.as_view()),
    path('route/<int:pk>', RoutesView.as_view()),
    path('map', StepsMapView.as_view())
]