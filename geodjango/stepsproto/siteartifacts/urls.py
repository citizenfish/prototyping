from django.contrib import admin
from django.conf import settings
from django.urls import path

from siteartifacts.views import AboutView, ContactView, PolicyView, HelpView

urlpatterns = [

    path('about', AboutView.as_view()),
    path('contact', ContactView.as_view()),
    path('policy', PolicyView.as_view()),
    path('help', HelpView.as_view())
]