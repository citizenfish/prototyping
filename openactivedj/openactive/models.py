from django.contrib.gis.db import models
from django.utils.timezone import now
from ckeditor.fields import RichTextField
from geocoder.geocoders import CoordinateGeocoder
from django.core.exceptions import ValidationError


class Parameter(models.Model):
    name = models.CharField('Parameter Name', max_length=50, unique=True)
    value = models.TextField('Parameter Value', null=True)
    jsonvalue = models.JSONField('JSON Value', null=True)

    # def save(self, *args, **kwargs):
    #     if self.value is None and self.jsonvalue is None:
    #         raise ValidationError("Either 'value' or 'jsonvalue' must be provided.")
    #     if self.value is not None and self.jsonvalue is not None:
    #         raise ValidationError("Only one of 'value' or 'jsonvalue' should be provided.")
    #
    #     super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class FeedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(enabled=True)


class Feed(models.Model):
    org = models.TextField('Organisation ID', primary_key=True)
    enabled = models.BooleanField('Enabled', default=True)
    metadata = models.JSONField('Meta data', null=True)
    discovered = models.DateTimeField('Discovery Date/Time', auto_now=True)
    lastload = models.DateTimeField('Last Loaded', null=True)

    feed_enabled = FeedManager()
    objects = models.Manager()

    class Meta:
        ordering = ['org']

    def __str__(self):
        return self.org


class FeedDistributionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(enabled=True)


class FeedDistribution(models.Model):
    dist_org = models.ForeignKey(Feed, on_delete=models.CASCADE, db_column='org')
    dist_name = models.URLField('Distribution Name')
    contenturl = models.URLField('Content URL', null=True)
    encoding = models.URLField('Encoding', null=True)
    additionaltype = models.URLField('AdditionalType', null=True)

    lastload = models.DateTimeField('Last Loaded', null=True)
    lasturl = models.URLField('Last URL Loaded', null=True)
    lastcount = models.IntegerField('Last Count Loaded', null=True, default=0)
    enabled = models.BooleanField('Enabled', default=True)
    metadata = models.JSONField('Meta data', null=True)
    errors = models.JSONField('Last errors', null=True)

    distribution_enabled = FeedDistributionManager()
    objects = models.Manager()

    class Meta:
        ordering = ['dist_org', 'dist_name']
        unique_together = [['dist_org', 'additionaltype']]

    def __str_(self):
        return self.type


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
    STATE_UPDATED = 'updated'
    STATE_DELETED = 'deleted'
    STATE_CHOICES = [
        (STATE_UPDATED, 'Updated'),
        (STATE_DELETED, 'Deleted'),
    ]

    title = models.CharField('Title', max_length=150)
    description = RichTextField('Description')
    eventurl = models.URLField('Event URL')
    images = models.JSONField('Images', null=True)

    organisername = models.TextField('Organiser', null=True)
    organiserurl = models.URLField('Organiser URL', null=True)
    location = models.PointField('Location', null=True)
    latitude = models.FloatField('Latitude', null=True)
    longitude = models.FloatField('Longitude', null=True)
    easting = models.IntegerField('Easting', null=True)
    northing = models.IntegerField('Northing', null=True)
    gridref = models.TextField('Grid Reference', null=True)
    locality = models.TextField('Locality', null=True)
    locationname = models.TextField('Location Name', null=True)
    locationaddress1 = models.CharField('Address 1', max_length=200, null=True)
    locationaddress2 = models.CharField('Address 2', max_length=200, null=True)
    locationaddress3 = models.CharField('Address 3', max_length=200, null=True)
    locationaddress4 = models.CharField('Address 4', max_length=200, null=True)
    locationaddress5 = models.CharField('Address 5', max_length=200, null=True)
    locationpostcode = models.CharField('Postcode', max_length=9, null=True)

    contactphone = models.CharField('Contact Telephone', max_length=50)
    contactemail = models.EmailField('Contact Email address', null=True)

    agemin = models.IntegerField('Minimum Age', default=0)
    agemax = models.IntegerField('Maximum Age', default=100)
    agestring = models.CharField('Age Descriptor', max_length=50, default='All Ages')

    eventdate = models.DateField('Event Date', null=True)
    eventdatestart = models.DateField('Event Date Start', null=True)
    eventdateend = models.DateField('Event Date End', null=True)
    eventtime = models.TimeField('Event Time', null=True)

    sourcetags = models.JSONField('Tags from source', null=True)
    systemtags = models.JSONField('System added tags', null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)

    state = models.CharField('State', max_length=10, choices=STATE_CHOICES, default=STATE_UPDATED)
    published = models.BooleanField('Published', default=False)
    online = models.BooleanField('Online', default=False)

    oa_org = models.CharField(max_length=255)
    oa_id = models.CharField(max_length=50)
    modified = models.BigIntegerField('Modified', default=0)
    license = models.TextField('License', null=True)
    rawdata = models.JSONField(null=True)

    class Meta:
        abstract = True
        ordering = ['eventdate', 'title']
        unique_together = [['oa_org', 'oa_id']]

    def process_oa_data(self):

        # Unpublish deleted
        if self.state == self.STATE_DELETED:
            self.published = False

        # Geocoding #TODO postcode and gridref
        if not self.location:
            if self.longitude and self.latitude:
                self.location = CoordinateGeocoder.geocode(self.longitude, self.latitude)

    def save(self, *args, **kwargs):
        self.process_oa_data()
        super(CoreOpenactiveTable, self).save(*args, **kwargs)

    def update(self, *args, **kwargs):
        self.process_oa_data()
        super(CoreOpenactiveTable, self).save(*args, **kwargs)

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


class ScheduledSession(CoreOpenactiveTable):
    class Meta:
        db_table = 'scheduledsession'
        unique_together = [['oa_org', 'oa_id']]


class League(CoreOpenactiveTable):
    class Meta:
        db_table = 'league'
        unique_together = [['oa_org', 'oa_id']]


class Slot(CoreOpenactiveTable):
    class Meta:
        db_table = 'slot'
        unique_together = [['oa_org', 'oa_id']]


class TagClassifier(models.Model):
    TYPE_CHOICES = [
        ('*', 'All'),
        ('Course', 'Course'),
        ('Course Instance', 'Course Instance'),
        ('Event', 'Event'),
        ('FacilityUse', 'Facility Use'),
        ('IndividualFacilityUse', 'Individual Facility Use'),
        ('OnDemandEvent', 'On Demand Event'),
        ('Session', 'Session'),
        ('SessionSeries', 'Session Series'),
        ('League', 'League'),
    ]
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    typefield_value = models.CharField('OpenActive Type', max_length=50, choices=TYPE_CHOICES)
    tagfield_values = models.JSONField('Item Tags')
