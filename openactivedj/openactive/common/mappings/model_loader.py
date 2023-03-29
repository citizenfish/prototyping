import traceback
from termcolor import colored
from urllib.parse import urljoin

from django.db.models import Q
from django.db import IntegrityError
from django.core import serializers

from openactive.models import FeedDistribution,Rule, apply_rules
from openactive.common.mappings.model_map import MODEL_MAP
from openactive.common.util.json import get_json
from openactive.common.util.map import openactive_item_mapper,kinds_count

from geocoder.geocoders import geocoder


class Loader:
    """
    The Loader class handles loading, geocoding and classification of OpenActive data.

    The class has the following optional initialisation parameters:-

    - types [event,course,..]: a list of types that will be loaded the default is all types
    - ignore_lasturl True/False: if set to true then all feed data will be loaded, otherwise the last url loaded will be used to initiate

    Data is loaded using the model_loader method

    The class relies on the dictionary MODEL_MAP to set mappings for each type that is loaded
    """

    def __init__(self, **kwargs):
        self.types = kwargs.get('types') if kwargs.get('types') else MODEL_MAP.keys()

        self.ignore_last_url = kwargs.get('ignore_lasturl', False)

        # These are state variables that change with each url loaded.
        self.urlerrors = []
        self.errors = []
        self.rpde_data = {}
        self.mapped_records = {}
        self.imports = {}
        self.org = None
        self.license = None
        self.url = None

        # This structure maps openactive schema to our internal model
        self.mappings = {key: value for key, value in MODEL_MAP.items() if
                         key in self.types} if self.types else MODEL_MAP

        # This holds the tag classification mappings, we load on class initiation to prevent a load every classification run.
        self.rules = Rule.objects.all()

        # Used in upsert query later, this is our primary key
        self.unique_fields = ['oa_org', 'oa_id']

        # These are the fields that will be updated if the record already exists on insert
        self.unique_keys = set()
        for k, v in MODEL_MAP.items():
            self.unique_keys.update({key for key in v.keys() if key not in self.unique_fields + ['model']})

    def model_loader(self, **kwargs):
        self.org = kwargs.get('org')
        print(f'Loading org {self.org}')

        # Retrieve the FeedDistributions for each org we are now down at the data level
        # Sorry about this next bit of code, blame openactive providers ...
        # we have to match 'event' to 'https://schema.org/Event' etc..

        q_objects = Q(additionaltype__isnull=True)
        for t in self.types:
            pattern = f'/{t}s?$'  # We need optional 's' at end to cope with ScheduledSessions/ScheduledSession
            q_objects |= Q(additionaltype__iregex=pattern)

        distributions = FeedDistribution.distribution_enabled.filter(dist_org=self.org).filter(
            q_objects)

        if len(distributions) == 0:
            self.errors.extend([{'model_loader': f'No distributions found for {self.org} with types {self.types}'}])
            return self.org, 0, self.errors

        org_count = 0
        for d in distributions:
            # We use the class variable as it traps errors
            self.url = d.lasturl if d.lasturl and not self.ignore_last_url else d.contenturl


            try:
                # Main distribution url processing loop
                urlcount = 0
                while self.url:
                    # Retrieve JSON data and the next url
                    self.url, lasturl = self.get_rpde_data()

                    if self.rpde_data:
                        # Map Data
                        m = self.map_rpde_data()
                        # No records mapped so move on to next url
                        if m == 0:
                            continue

                        # Geocode Data
                        self.geocode_rpde_data()

                        # Classify Data
                        self.classify_rpde_data()

                        # Load Data
                        urlcount += self.load_rpde_data()

                org_count += urlcount

                # UPDATE Feed Distribution record, lasturl is important as we begin fetching from there next time
                if urlcount > 0:
                    d.lasturl = lasturl
                    d.errors = self.urlerrors
                    d.save()
                    self.errors.extend(self.urlerrors)
                    self.urlerrors = []

            except Exception as e:
                error_trace = traceback.format_exc()
                self.error_handler(func='model_loader',
                                   err=f'{str(e)}: {error_trace[:100]}',
                                   url=self.url)

        return self.org, org_count, self.errors

    def get_rpde_data(self, **kwargs):

        print(f'get_rpde_data for {self.url}')
        self.rpde_data = {}

        rpde_data = get_json(self.url)
        items = rpde_data.get('items', [])

        # No data retrieved so return empty handed
        if not rpde_data or not items:
            return None, self.url

        self.rpde_data = items
        self.license = rpde_data.get('license')

        # The RPDE specification states that the next url must be an absolute url, this is not always adhered to so
        # this copes with it
        return urljoin(self.url, rpde_data.get('next')), self.url

    def map_rpde_data(self, **kwargs):
        print(f'map_rpde_data {len(self.rpde_data)} items')

        # Initialise with the types as top level keys
        self.mapped_records = {key: [] for key, value in self.mappings.items()}

        for r in self.rpde_data:
            kind, record = openactive_item_mapper(item=r,
                                                  mappings=self.mappings,
                                                  org=self.org,
                                                  license=self.license)
            if kind:
                self.mapped_records[kind].append(record)

        return kinds_count(self.mapped_records)

    def geocode_rpde_data(self, **kwargs):
        print(f'geocode_rpde_data {kinds_count(self.mapped_records)} items')

        for kind in self.mapped_records:
            self.imports[kind] = []
            model = self.mappings[kind]['model']
            for item in self.mapped_records[kind]:
                # No point trying to geocode stuff that's getting deleted
                if item['state'] != 'deleted':
                    item['location'] = geocoder(item)

                # Now we make an ORM object ready for database import
                self.imports[kind].append(model(**item))

        return kinds_count(self.imports)

    """
    Must happen after geocoding as we operate on objects not dictionary values
    """
    def classify_rpde_data(self, **kwargs):
        count = kinds_count(self.imports)
        print(f'classify_rpde_data {count} items')
        # We iterate through the items and call the function apply_rules imported from the model

        if self.rules:
            for kind in self.imports:
                model = self.mappings[kind]['model']
                # This is manually calling the trigger
                for item in self.imports[kind]:
                    apply_rules(item, model, self.rules)

        else:
            print('No classification rules set')

        return count


    def load_rpde_data(self, **kwargs):
        print(f'load_rpde_data: {kinds_count(self.imports)} items')
        result = []
        for kind in self.imports:
            records = self.imports[kind]
            if len(records) > 0:
                model = self.mappings[kind]['model']
                try:
                    result = model.objects.bulk_create(records,
                                                       update_conflicts=True,
                                                       unique_fields=self.unique_fields,
                                                       update_fields=self.unique_keys)
                except Exception as e:
                    # Try for individual records and trap the one that failed
                    for r in records:
                        try:
                            r.save()
                        except IntegrityError as e:
                            error_trace = traceback.format_exc()
                            self.error_handler(func='load_rpde_data',
                                               err=f'{str(e)}: {error_trace[:100]}',
                                               packet=serializers.serialize('json', r),
                                               url=self.url)
                            continue

        return len(result)

    def error_handler(self, **kwargs):
        errstr = f"[{kwargs.get('url')}] - {kwargs.get('func')} - {kwargs.get('err')}"
        print(colored(errstr, 'red'))
        self.urlerrors.append({self.url: kwargs})

    def list_mappings(self):
        return list(self.mappings.keys())

    def truncate_all(self):

        for model_key in self.mappings:
            model = self.mappings[model_key]['model']
            model.objects.all().delete()

        return f'Truncated {self.list_mappings()}'

    def remove_deleted(self):

        for model_key in self.mappings:
            model = self.mappings[model_key]['model']
            model.objects.filter(state='deleted').delete()

        return f'Removed deleted items from {self.list_mappings()}'
