from django.contrib.gis import admin

from steps.models import Step, Route, StepImage, Walk

from django.conf import settings

defs = {
        'attrs': {
            'default_zoom' : settings.DEFAULT_MAP_ZOOM,
            'default_lon': settings.DEFAULT_MAP_LON,
            'default_lat' : settings.DEFAULT_MAP_LAT
        }
    }

## Do not register this class as you will get an error, you only need to register stuff going on menu
class StepImage(admin.TabularInline):
    model = StepImage

@admin.register(Step)
class StepAdmin(admin.GISModelAdmin):
    # TODO maintain in settings
    gis_widget_kwargs = defs
    list_display = ('name', 'location', 'text', 'audio')
    inlines = [StepImage]

@admin.register(Route)
class RouteAdmin(admin.GISModelAdmin):
    gis_widget_kwargs = defs
    list_display = ('name', 'startpoint', 'endpoint', 'startname', 'endname')
    filter_horizontal = ('steps',)

@admin.register(Walk)
class WalkAdmin(admin.GISModelAdmin):
    list_display = ('name','text', 'image')
    filter_horizontal = ('route',)
