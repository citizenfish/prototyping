from django.contrib.gis.db import models
from ordered_model.models import OrderedModel
from ckeditor.fields import RichTextField

class Step(models.Model):
    name = models.CharField('Name of steps', max_length=200)
    text = RichTextField('Description')
    location = models.PointField()
    audio = models.FileField(default='', null=True, blank=True) # <audio src="{{ song.file.url }}" controls></audio> in template
    icon = models.CharField('Icon', default='step', max_length=20)
    class Meta:
        ordering = ['name']
    def __str__(self):
        return self.name

class Route(models.Model):
    name = models.CharField('Name of route', max_length=50)
    text = RichTextField('Route Description')
    steps = models.ManyToManyField(Step)
    startpoint = models.PointField('Route Start')
    endpoint = models.PointField('Route End')
    startname = models.CharField("Route Start", max_length=50)
    endname = models.CharField('Route End', max_length=50)
    icon = models.CharField('Icon', default='route', max_length=20)

    class Meta:
        ordering = ['name']
    def __str__(self):
        return self.name

class RouteInstruction(OrderedModel):
    locationname = models.CharField('Instruction Location', max_length=100)
    instruction = RichTextField('Instruction',max_length=500,default='')
    location = models.PointField(null=True,blank=True)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    order_with_respect_to = "route" # critical for arrows to work in admin
    icon = models.CharField('Icon', default='direction', max_length=20)
    def __str__(self):
        return self.locationname

class StepImage(models.Model):
    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    image = models.ImageField()
    alttext = models.CharField(default='An image of a step', max_length=50)

class Walk(models.Model):
    name = models.CharField('Name of walk type', max_length=50)
    text = models.TextField('Description')
    route = models.ManyToManyField(Route)
    image = models.ImageField()

    def __str__(self):
        return self.name

