from django.contrib import admin

from siteartifacts.models import AboutPage, PolicyPage, HelpPage, HelpItem, IndexPage, SiteImage

class SiteImage(admin.TabularInline):
    model = SiteImage
@admin.register(IndexPage)
class IndexPage(admin.ModelAdmin):
    list_display = ('strapline', 'summarytext', 'text')
    inlines = [SiteImage]

@admin.register(AboutPage)
class AboutPage(admin.ModelAdmin):
    list_display = ('linktext', 'summarytext', 'pagetext', 'image')

@admin.register(PolicyPage)
class PolicyPage(admin.ModelAdmin):
    list_display = ('linktext','summarytext','pagetext')

@admin.register(HelpPage)
class HelpPage(admin.ModelAdmin):
    list_display = ('linktext', 'summarytext', 'pagetext')
    filter_horizontal = ('helpitems',)

@admin.register(HelpItem)
class HelpItem(admin.ModelAdmin):
    list_display = ('linktext', 'summarytext', 'pagetext', 'image')

