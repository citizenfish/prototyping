from django.core.management.base import BaseCommand
from openactive.common.mappings.model_loader import Loader
from openactive.models import Feed
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.db.models.expressions import RawSQL
from django.db import connection
from datetime import datetime
import pytz


class Command(BaseCommand):
    help = 'Imports data from an OpenActive API'

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.loader = Loader()
        self.providers = []
        self.ignore_lasturl = True

    def add_arguments(self, parser):
        parser.add_argument(
            '--reload',
            action='store_true',
            help='Delete all existing data and reload',
            required=False,
            default=False
        )

        parser.add_argument(
            '--reload_no_warning',
            action='store_true',
            help='Delete all existing data and reload with no warning prompt',
            required=False,
            default=False
        )

        parser.add_argument(
            '--types',
            dest='types',
            help='A comma separated subset of Openactive types to process',
            required=False,
            default=None
        )

        parser.add_argument(
            '--org',
            dest='org',
            help='A single organisation id to load',
            required=False,
            default=None
        )

        parser.add_argument(
            '--threads',
            dest='threads',
            type=int,
            help='Number of threads',
            required=False,
            default=4
        )

        parser.add_argument(
            '--timezone',
            dest='timezone',
            type=str,
            help='Timezone default: Europe/London ',
            required=False,
            default='Europe/London'
        )

    def handle(self, *args, **options):

        # First decide which openactive types we are operating on
        types = options['types']
        if types:
            types = types.lower().split(',')

        # The Loader class contains various convenience methods for mapping/Loading Openactive fields and other
        # processing utilities
        self.loader = Loader(types=types)
        self.stdout.write(self.style.NOTICE(f'Loading {self.loader.list_mappings()}'))

        # Next are we doing a complete reload or an update
        if options['reload'] or options['reload_no_warning']:
            self.truncate_all(options['reload_no_warning'])
            self.ignore_lasturl = True

        # Now get the list of providers unless we are loading only one
        self.providers = [options['org']] if options['org'] else self.get_feeds()

        # Main processing loop running in a multithreading environment to speed things up
        with ThreadPoolExecutor(max_workers=options['threads']) as executor:
            futures = [executor.submit(self.process_url, org=org, types=types, ignore_lasturl=self.ignore_lasturl,
                                       timezone=options['timezone']) for
                       org in self.providers]

        # Capture results of each thread and update the org records
        for future in as_completed(futures):
            org, count, errors = future.result()
            self.stdout.write(self.style.SUCCESS(f'Loaded {count} for {org} with {len(errors)} errors'))

        # Remove all deleted items
        self.loader.remove_deleted()
        self.stdout.write(self.style.SUCCESS(f'Removed deleted items from {self.loader.list_mappings()}'))

    @staticmethod
    def process_url(**kwargs):
        # Close existing connection to ensure we get a connection for each thread
        connection.close()
        loader = Loader(**kwargs)
        org, count, errors = loader.model_loader(org=kwargs['org'])

        # Get the current date and time
        now = datetime.now(pytz.timezone(kwargs.get('timezone')))

        # Format the date and time as a string to be used as a key in metadata
        key_to_update = now.strftime('%Y-%m-%d_%H_%M_%S')

        # Make an update record to add to the Feed and update it
        metadata = {'errors': errors, 'count': count}

        Feed.objects.filter(org=org).update(
            metadata=RawSQL(
                "jsonb_set(metadata, %s, %s)",
                ([key_to_update], metadata)
            ),
            lastload=now
        )

        return org, count, errors

    def truncate_all(self, no_warning):
        if not no_warning:
            s = input(f'Delete ALL loaded OpenActive data for {self.loader.list_mappings()} [y/N]')
            if s[0].lower() != 'y':
                exit()

        self.stdout.write(self.style.WARNING('*** Deleting all OpenActive data ***'))
        self.stdout.write(self.style.NOTICE(self.loader.truncate_all()))

    @staticmethod
    def get_feeds():
        feeds = []
        for f in Feed.feed_enabled.all().values('org'):
            feeds.append(f['org'])
        return feeds
