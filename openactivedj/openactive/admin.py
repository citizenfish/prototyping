from django.contrib.gis import admin
from openactive.models import Category, Event, Parameter, Feed, FeedDistribution, Category, Rule, Event


# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.GISModelAdmin):
    list_display = ('name', 'description')


@admin.register(Event)
class EventAdmin(admin.GISModelAdmin):
    list_display = ('oa_id', 'oa_org', 'title', 'description','category','sourcetags', 'systemtags')
    search_fields = ['title']

@admin.register(Parameter)
class ParametersAdmin(admin.GISModelAdmin):
    list_display = ('name', 'value')


class FeedDistributionInline(admin.TabularInline):
    model = FeedDistribution
@admin.register(Feed)
class OpenActiveFeedsAdmin(admin.GISModelAdmin):
    list_display = ('org', 'metadata')
    inlines = [FeedDistributionInline]


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ('category','systemtagfield_value','rule_type','regex_search')



