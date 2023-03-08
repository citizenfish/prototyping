from django.db import models
from ckeditor.fields import RichTextField


class AboutPage(models.Model):
    linktext = models.CharField('Link Text', max_length=15)
    summarytext = RichTextField('Summary Text', max_length=300)
    pagetext = RichTextField('Main Body Text')
    image = models.ImageField()

class PolicyPage(models.Model):
    # There is some repetition here but I want a separate item in the admin backend
    linktext = models.CharField('Link Text', max_length=15)
    summarytext = RichTextField('Summary Text', max_length=300)
    pagetext = RichTextField('Main Body Text')

class HelpItem(models.Model):
    linktext = models.CharField('Link Text', max_length=15)
    summarytext = RichTextField('Summary Text', max_length=300)
    pagetext = RichTextField('Main Body Text')
    image = models.ImageField()

class HelpPage(models.Model):
    linktext = models.CharField('Link Text', max_length=15)
    summarytext = RichTextField('Summary Text', max_length=300)
    pagetext = RichTextField('Main Body Text')
    helpitems = models.ManyToManyField(HelpItem)

class IndexPage(models.Model):
    strapline = models.CharField('Strap Line', max_length=200)
    summarytext = RichTextField('Summary Text', max_length=300)
    text = RichTextField('Main Body Text')

class SiteImage(models.Model):
    step = models.ForeignKey(IndexPage, on_delete = models.CASCADE)
    image = models.ImageField()
    alttext = models.CharField(max_length=200, default='An image on the site fromt page')