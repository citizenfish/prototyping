import re
from django.contrib.gis.db import models
from ckeditor.fields import RichTextField
from geocoder.geocoders import CoordinateGeocoder
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.html import strip_tags

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
        return self.dist_org


class Tags(models.Model):
    tag = models.CharField('Tag', max_length=50)

    description = RichTextField('Tag Description')

    class Meta:
        ordering = ['tag']
        unique_together = ['tag']

    def __str__(self):
        return self.tag


class Category(models.Model):
    name = models.CharField("Category Name", max_length=50, unique=True)
    description = RichTextField('Category Description', null=True)
    image = models.ImageField('Category Image', null=True)

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

    title = models.TextField('Title')
    description = RichTextField('Description')
    eventurl = models.URLField('Event URL')
    images = models.JSONField('Images', null=True, blank=True)

    organisername = models.TextField('Organiser', null=True, blank=True)
    organiserurl = models.URLField('Organiser URL', null=True, blank=True)
    location = models.PointField('Location', null=True, blank=True)
    latitude = models.FloatField('Latitude', null=True, blank=True)
    longitude = models.FloatField('Longitude', null=True, blank=True)
    easting = models.IntegerField('Easting', null=True, blank=True)
    northing = models.IntegerField('Northing', null=True, blank=True)
    gridref = models.TextField('Grid Reference', null=True, blank=True)
    locality = models.TextField('Locality', null=True, blank=True)
    locationname = models.TextField('Location Name', null=True, blank=True)
    locationaddress1 = models.TextField('Address 1', null=True, blank=True)
    locationaddress2 = models.TextField('Address 2', null=True, blank=True)
    locationaddress3 = models.TextField('Address 3', null=True, blank=True)
    locationaddress4 = models.TextField('Address 4', null=True, blank=True)
    locationaddress5 = models.TextField('Address 5', null=True, blank=True)
    locationpostcode = models.CharField('Postcode', max_length=15, null=True, blank=True)

    contactphone = models.CharField('Contact Telephone', max_length=100, blank=True)
    contactemail = models.EmailField('Contact Email address', null=True, blank=True)

    agemin = models.IntegerField('Minimum Age', default=0, blank=True)
    agemax = models.IntegerField('Maximum Age', default=100, blank=True)
    agestring = models.CharField('Age Descriptor', max_length=50, default='All Ages', blank=True)

    eventdate = models.DateField('Event Date', null=True, blank=True)
    eventdatestart = models.DateField('Event Date Start', null=True, blank=True)
    eventdateend = models.DateField('Event Date End', null=True, blank=True)
    eventtime = models.TimeField('Event Time', null=True, blank=True)

    sourcetags = models.JSONField('Tags from source', null=True, blank=True)
    systemtags = models.JSONField('System added tags', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)

    state = models.CharField('State', max_length=10, choices=STATE_CHOICES, default=STATE_UPDATED)
    published = models.BooleanField('Published', default=False)
    online = models.BooleanField('Online', default=False)

    oa_org = models.CharField(max_length=255)
    oa_id = models.CharField(max_length=255)
    modified = models.CharField('Modified', max_length=255)
    license = models.TextField('License', null=True, blank=True)
    rawdata = models.JSONField(null=True, blank=True)

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

    # used for Elasticsearch which will not index ckeditor fields
    def description_as_text(self):
        if self.description:
            return strip_tags(self.description)

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


class Rule(models.Model):
    RULE_TYPE_CHOICES = (
        ('title_regex', 'Regular Expression (Title)'),
        ('desc_regex', 'Regular Expression (Description)'),
        ('tag', 'Tag')
    )

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    systemtagfield_value = models.CharField(max_length=50)
    sourcetagfield_values = models.JSONField(blank=True,null=True)
    regex_search = models.TextField('Regex to find', null=True)
    rule_type = models.CharField(max_length=15, choices=RULE_TYPE_CHOICES, default='tag')


"""
Classify items using the rules in the Rule model, can be called with rules from bulk load process or retrieve rules
This code will set systemtags if a rule match is found and/or set the category for an item
"""

def apply_rules(item, sender, rules=None):
    saveitem = True if not rules else False
    rules = rules if rules else Rule.objects.all()
    changed = False
    item.systemtags = item.systemtags if item.systemtags else []

    for rule in rules:
        matching_tags = []
        match = False

        if rule.rule_type == 'tag' and item.sourcetags:
            matching_tags = set(tag.lower() for tag in item.sourcetags).intersection(
                tag.lower() for tag in rule.sourcetagfield_values)

        if rule.rule_type == 'title_regex':
            match = bool(re.search(rule.regex_search, item.title, re.IGNORECASE))

        if rule.rule_type == 'desc_regex':
            match = bool(re.search(rule.regex_search, item.description, re.IGNORECASE))

        if len(matching_tags) > 0 or match:
            changed = True
            if rule.systemtagfield_value:
                item.systemtags.extend([rule.systemtagfield_value])
            # Do not overwrite a category that has already been set
            # Note well that the first match will win
            if item.category is None and rule.category is not None:
                item.category = rule.category

    # Do not save if rules passed in as we are in bulk mode
    if saveitem and changed:
        # we have to disable the post_save receiver to prevent it being called again
        post_save.disconnect(apply_rules_on_item_creation, sender=sender)
        item.save()
        post_save.connect(apply_rules_on_item_creation, sender=sender)


# TODO add for other models
@receiver(post_save, sender=Event)
def apply_rules_on_item_creation(sender, instance, created, **kwargs):
    apply_rules(instance, sender)
