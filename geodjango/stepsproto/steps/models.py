
from django.contrib.gis.db import models

# Basic steps model

class Step(models.Model):
    name = models.CharField('Name of steps', max_length=200)
    text = models.TextField('Description')
    location = models.PointField()
    audio = models.FileField(default='') # <audio src="{{ song.file.url }}" controls></audio> in template

    class Meta:
        ordering = ['name']
    def __str__(self):
        return self.name
class Route(models.Model):
    name = models.CharField('Name of route', max_length=50)
    text = models.TextField('Route Description')
    steps = models.ManyToManyField(Step)
    startpoint = models.PointField('Route Start')
    endpoint = models.PointField('Route End')
    startname = models.CharField("Route Start", max_length=50)
    endname = models.CharField('Route End', max_length=50)

    class Meta:
        ordering = ['name']
    def __str__(self):
        return self.name

class StepImage(models.Model):
    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    image = models.ImageField()

class Walk(models.Model):
    name = models.CharField('Name of walk type', max_length=50)
    text = models.TextField('Description')
    route = models.ManyToManyField(Route)
    image = models.ImageField()

    def __str__(self):
        return self.name

