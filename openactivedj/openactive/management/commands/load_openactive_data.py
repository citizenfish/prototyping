import requests
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from openactive.models import Course, Event, CourseInstance, FacilityUse, OnDemandEvent

class Command(BaseCommand):
    help = 'Imports data from an OpenActive API'

    MODEL_MAP = {
        'course': {
            'title': 'title',
            'description': 'description',
            'oa_id': 'oa_id',
            'oa_org': 'oa_org'
        },
        'event': {
            'title': 'event.title',
            'description': 'event.description',
            'oa_id': 'id',
            'modified':'modified',
            'state':'state'
        },
        'courseinstance': {
            'title': 'name',
            'description': 'description',
            'oa_id': 'identifier'
        },
        'facilityuse': {
            'title': 'name',
            'description': 'description',
            'oa_id': 'identifier'
        },
        'ondemandevent': {
            'title': 'event.title',
            'description': 'event.description',
            'oa_id': 'event.id'
        }
    }

    def add_arguments(self, parser):
        parser.add_argument('url', type=str, help='The OpenActive API URL to fetch data from')
        parser.add_argument('org', type=str, help='The OpenActive oa_org for this organisation')

    def handle(self, *args, **options):
        url = options['url']
        res = requests.get(url)
        jsonres = res.json()
        items = jsonres.get('items')

        courses = []
        events = []
        course_instances = []
        facility_uses = []
        on_demand_events = []

        for item in items:
            item['oa_org'] = options['org']
            item_type = item.get('kind').lower()

            if item_type == 'course':
                course_data = {k: item.get(v) for k, v in self.MODEL_MAP[item_type].items()}
                course_data['location'] = Point(float(item['location']['longitude']), float(item['location']['latitude']))
                courses.append(Course(**course_data))

            elif item_type == 'event':
                event_data = {k: item.get(v) for k, v in self.MODEL_MAP[item_type].items()}
                event_data['location'] = Point(float(item['location']['longitude']), float(item['location']['latitude']))
                events.append(Event(**event_data))

            elif item_type == 'courseinstance':
                course_instance_data = {k: item.get(v) for k, v in self.MODEL_MAP[item_type].items()}
                course_instances.append(CourseInstance(**course_instance_data))

            elif item_type == 'facilityuse':
                facility_use_data = {k: item.get(v) for k, v in self.MODEL_MAP[item_type].items()}
                facility_uses.append(FacilityUse(**facility_use_data))

            elif item_type == 'ondemandevent':
                on_demand_event_data = {k: item.get(v) for k, v in self.MODEL_MAP[item_type].items()}
                on_demand_events.append(OnDemandEvent(**on_demand_event_data))

            else:
                print(f'Cannot deal with {item_type}')
                exit()

        Course.objects.bulk_create(courses)
        Event.objects.bulk_create(events)
        CourseInstance.objects.bulk_create(course_instances)
        FacilityUse.objects.bulk_create(facility_uses)
        OnDemandEvent.objects.bulk_create(on_demand_events)

        self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(items)} items from {url}'))
