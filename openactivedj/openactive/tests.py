from django.test import TestCase
from openactive.models import Event, Category
import requests
import timeit
import os
from django.db import transaction
# Create your tests here.

class EventModelTests(TestCase):

    def test_insert_one_event(self):
        event = Event(
                    oa_id='12345',
                    oa_org='https://aaaa.com',
                    rawdata={'foo':'baa'},
                    title='TEST Title UPDATE UPSERT',
                    description='TEST Description',
                    eventurl='http://test.com',
                    sourcetags=['cycling']
                )

        event.save()
        self.assertIsNotNone(event.category_id)


    # @transaction.non_atomic_requests
    # def test_insert_500_from_better(self):
    #     url = 'https://www.better.org.uk/odi/sessions.json?afterTimestamp=1677492276&afterId=64925075'
    #     print('Downloading Data')
    #     res = requests.get(url)
    #
    #     if os.environ.get('EVENTS_truncate', '') == 'true':
    #         print('Truncating events')
    #         Event.objects.all().delete()
    #
    #     events_count = Event.objects.count()
    #
    #     print(f'Begin with {events_count} loaded')
    #     start_time = timeit.default_timer()
    #     jsonres = res.json()
    #     items = jsonres.get('items')
    #     org = 'http://data.better.org.uk/'
    #     events = []
    #     for f in items:
    #         kind = f.get('kind')
    #         creates = ()
    #         if kind == 'Event' and os.environ.get('EVENTS_single_trans') == 'true':
    #             print('single item load')
    #             obj, created = Event.objects.update_or_create(
    #                 oa_id=f.get('id'),
    #                 oa_org=org,
    #                 defaults={
    #                     'rawdata': f,
    #                     'title': 'TEST Title UPDATE 12.5',
    #                     'description': 'TEST Description',
    #                     'eventurl': 'TEST EVENT URL',
    #                     'category_id': 1,
    #                     'latitude': f.get('data', {}).get('location', {}).get('geo', {}).get('latitude'),
    #                     'longitude': f.get('data', {}).get('location', {}).get('geo', {}).get('longitude')
    #                 }
    #             )
    #
    #         if kind == 'Event' and os.environ.get('EVENTS_filter_trans') == 'true':
    #
    #             event = Event.objects.filter(oa_id=f.get('id'), oa_org=org).first()
    #             if event:
    #                 # Update the event data
    #                 event.rawdata = f
    #                 event.title = 'TEST Title UPDATE 12.5'
    #                 event.description = 'TEST Description'
    #                 event.eventurl = 'TEST EVENT URL'
    #                 event.category_id = 1
    #                 event.latitude = f.get('data', {}).get('location', {}).get('geo', {}).get('latitude')
    #                 event.longitude = f.get('data', {}).get('location', {}).get('geo', {}).get('longitude')
    #
    #             else:
    #                 # Create a new event
    #                 event = Event(
    #                     oa_id=f.get('id'),
    #                     oa_org=org,
    #                     rawdata=f,
    #                     title='TEST Title UPDATE UPSERT',
    #                     description='TEST Description',
    #                     eventurl='TEST EVENT URL',
    #                     category_id=1,
    #                     latitude=f.get('data', {}).get('location', {}).get('geo', {}).get('latitude'),
    #                     longitude=f.get('data', {}).get('location', {}).get('geo', {}).get('longitude')
    #                 )
    #
    #             events.append(event)
    #
    #         if kind == 'Event' and os.environ.get('EVENTS_bulk_update') == 'true':
    #             event = Event(
    #                 oa_id=f.get('id'),
    #                 oa_org=org,
    #                 rawdata=f,
    #                 title='TEST Title UPDATE 15',
    #                 description='TEST Description',
    #                 eventurl='TEST EVENT URL',
    #                 category_id=1,
    #                 latitude=f.get('data', {}).get('location', {}).get('geo', {}).get('latitude'),
    #                 longitude=f.get('data', {}).get('location', {}).get('geo', {}).get('longitude')
    #             )
    #
    #             events.append(event)
    #
    #      # Use the bulk_sync method to synchronize the events list with the database
    #     if os.environ.get('EVENTS_filter_trans') == 'true':
    #         with transaction.atomic():
    #             bulk_sync(events, Event.objects.all(), ['oa_id', 'oa_org'])
    #
    #     if os.environ.get('EVENTS_bulk_update') == 'true':
    #         print(f'UPSERTING {len(events)} Events')
    #         objs = Event.objects.bulk_create([events[0]], update_conflicts=True, unique_fields=['oa_org','oa_id'], update_fields=['rawdata','title','description', 'eventurl', 'latitude', 'longitude'])
    #
    #     end_time = timeit.default_timer()
    #     print(f"Test execution time: {end_time - start_time} seconds.")
    #     events_insert_count = Event.objects.count() - events_count
    #     print(f'ENDED with {events_insert_count} loaded')
    #
