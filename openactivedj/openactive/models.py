from django.contrib.gis.db import models
from ckeditor.fields import RichTextField

class Tags(models.Model):
    tag = models.CharField('Tag', max_length=50)
    description = RichTextField('Tag Description')

    class Meta:
        ordering = ['tag']
        unique_together = ['tag']

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField("Category Name", max_length=50)
    description = RichTextField('Category Description')
    image = models.ImageField('Category Image')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class CoreOpenactiveTable(models.Model):

    title = models.CharField('Title', max_length=150)
    description = RichTextField('Description')
    eventurl = models.URLField('Event URL')
    images = models.JSONField('Images',null=True)

    organisername = models.CharField('Organiser', max_length=100)
    organiserurl = models.URLField('Organiser URL',null=True)
    location = models.PointField('Location', null=True)
    locationname = models.CharField('Location Name', max_length=100,null=True)
    locationaddress1 = models.CharField('Address 1', max_length=200,null=True)
    locationaddress2 = models.CharField('Address 2', max_length=200,null=True)
    locationaddress3 = models.CharField('Address 3', max_length=200,null=True)
    locationaddress4 = models.CharField('Address 4', max_length=200,null=True)
    locationaddress5 = models.CharField('Address 5', max_length=200,null=True)
    locationPostcode = models.CharField('Postcode', max_length=9,null=True)

    contactphone = models.CharField('Contact Telephone', max_length=20)
    contactemail = models.EmailField('Contact Email address',null=True)

    agemin = models.IntegerField('Minimum Age', default=0)
    agemax = models.IntegerField('Maximum Age', default=100)
    agestring = models.CharField('Age Descriptor', max_length=50, default='All Ages')

    eventdate = models.DateField('Event Date', null=True)
    eventdatestart = models.DateField('Event Date Start', null=True)
    eventdateend = models.DateField('Event Date End', null=True)
    eventtime = models.TimeField('Event Time', null=True)

    tags = models.ManyToManyField(Tags,related_name="+")

    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    published = models.BooleanField('Published',default=False)
    online = models.BooleanField('Online',default=False)

    oa_org = models.CharField(max_length=255)
    oa_id = models.CharField(max_length=50)

    rawdata = models.JSONField()

    class Meta:
        abstract = True
        ordering = ['eventdate','title']
        unique_together = [['oa_org', 'oa_id']]

    def __str__(self):
        return self.title


class Course(CoreOpenactiveTable):

    class Meta:
        db_table = 'course'
        unique_together = [['oa_org', 'oa_id']]

class CourseInstance(CoreOpenactiveTable):

    class Meta:
        db_table = 'courseinstance'
        unique_together = [['oa_org', 'oa_id']]

class Event(CoreOpenactiveTable):

    class Meta:
        db_table = 'event'
        unique_together = [['oa_org', 'oa_id']]

class FacilityUse(CoreOpenactiveTable):

    class Meta:
        db_table = 'facilityuse'
        unique_together = [['oa_org', 'oa_id']]

class IndividualFacilityUse(CoreOpenactiveTable):

    class Meta:
        db_table = 'individualfacilityuse'
        unique_together = [['oa_org', 'oa_id']]


class OnDemandEvent(CoreOpenactiveTable):
    online = models.BooleanField('Online', default=True)
    class Meta:
        db_table = 'ondemandevent'
        unique_together = [['oa_org', 'oa_id']]

class Session(CoreOpenactiveTable):

    class Meta:
        db_table = 'session'
        unique_together = [['oa_org', 'oa_id']]


class SessionSeries(CoreOpenactiveTable):
    class Meta:
        db_table = 'sessionseries'
        unique_together = [['oa_org', 'oa_id']]