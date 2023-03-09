from django.contrib.gis import admin
from ordered_model.admin import OrderedStackedInline, OrderedInlineModelAdminMixin
from steps.models import Step, Route, StepImage, Walk, RouteInstruction

# Done as we are overriding edit widget for Route Instructions
from django.contrib.gis.forms.widgets import OSMWidget
from django.contrib.gis.db import models
from django.conf import settings

defs = {
    'attrs': {
        'default_zoom': settings.DEFAULT_MAP_ZOOM,
        'default_lon': settings.DEFAULT_MAP_LON,
        'default_lat': settings.DEFAULT_MAP_LAT
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

class RouteInstructionAdmin(OrderedStackedInline):
    model = RouteInstruction
    gis_widget_kwargs = defs
    fields=('locationname', 'instruction', 'location','order', 'move_up_down_links',)
    readonly_fields = ('order', 'move_up_down_links',)
    ordering = ('order',)
    extra = 1
    # necessary otherwise it defaults to GEOModelAdmin
    formfield_overrides = {
        models.PointField: {"widget": OSMWidget(attrs=defs['attrs'])}
    }

@admin.register(Route)
class RouteAdmin(OrderedInlineModelAdminMixin, admin.GISModelAdmin):
    gis_widget_kwargs = defs
    list_display = ('name', 'startpoint', 'endpoint', 'startname', 'endname')
    filter_horizontal = ('steps',)

    inlines=[RouteInstructionAdmin]

@admin.register(Walk)
class WalkAdmin(admin.GISModelAdmin):
    list_display = ('name', 'text', 'image')
    filter_horizontal = ('route',)
