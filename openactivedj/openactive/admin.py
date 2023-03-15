from django.contrib.gis import admin
from openactive.models import Category,Event

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.GISModelAdmin):
    list_display = ('name','description')

@admin.register(Event)
class EventAdmin(admin.GISModelAdmin):
    list_display = ('oa_id', 'oa_org', 'title', 'description')

