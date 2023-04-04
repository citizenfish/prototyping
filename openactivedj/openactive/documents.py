from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from openactive.models import Event, CourseInstance, SessionSeries, ScheduledSession, FacilityUse, \
    IndividualFacilityUse, League, CoreOpenactiveTable

# Register our documents for elasticsearch searching

@registry.register_document
class EventDocument(Document):
    # Use the richtext_to_string method in model to convert to textfield and add it to the fields
    description = fields.TextField(attr='description_as_text')

    class Index:
        name = 'openactive'

    settings = {
        'number_of_shards': 1,
        'number_of_replicas': 0
    }

    class Django:
        model = CoreOpenactiveTable
        fields = ['title']
