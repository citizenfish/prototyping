from django.test import TestCase
from openactive.models import Event, Category
import requests
import json

# Create your tests here.

url = 'https://www.better.org.uk/odi/sessions.json?afterTimestamp=1677492276&afterId=64925075'
res = requests.get(url)
jsonres = res.json()
items = jsonres.get('items')
org = 'http://data.better.org.uk/'
for f in items:
    kind = f.get('kind')
    creates = ()
    if kind == 'Event':
        obj, created = Event.objects.update_or_create(
            oa_id=f.get('id'),
            oa_org=org,
            defaults={
                'rawdata': f,
                'title': 'TEST Title UPDATE 12.5',
                'description': 'TEST Description',
                'eventurl': 'TEST EVENT URL',
                'category_id': 1
            }
        )
