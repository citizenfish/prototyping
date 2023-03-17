from openactive.common.util.json import get_json, get_json_ld
from django.core.management.base import BaseCommand, CommandError
from openactive.models import Parameter, OpenActiveFeed


class Command(BaseCommand):
    help = 'Discover OpenActive feeds and populate'
    url = 'https://openactive.io/data-catalogs/data-catalog-collection.jsonld'

    def add_arguments(self, parser):
        parser.add_argument(
            '-openactive_discovery_url',
            dest='openactive_discovery_url',
            type=str,
            help='URL to discover feeds from',
            required=False,
        )
        parser.add_argument(
            '-excluded_feeds',
            dest='excluded_feeds',
            type=str,
            help='Feeds to exclude',
            required=False,
        )

    def handle(self, *args, **options):
        print('Discovering OpenActive feeds')

        # Can exclude organisations if we want
        excluded_feeds = options.get('excluded_feeds', '')
        excluded_feeds = excluded_feeds.split(',') if excluded_feeds else []
        # We need a catalog url to work out from
        url = options.get('openactive_discovery_url')
        if not url:
            try:
                url = Parameter.objects.get(name='openactive_discovery_url').value
            except  Parameter.DoesNotExist:
                raise CommandError('openactive_discovery_url has not been defined in parameters or command line')

        # First we pull our list of catalogues
        catalogues = get_json(url, 'hasPart')
        if not catalogues:
            raise CommandError(f'Nothing found at {url} {catalogues}')

        for hasPart in catalogues:

            # We retrieve the metadata for each catalogue this is an embedded script in a HTML page :-(
            data_catalogues = get_json(hasPart, 'dataset')
            #
            for dataSet in data_catalogues:
                metadata = get_json_ld(dataSet)
                if metadata:
                    feed_type = metadata.get('@type')
                    # We are only loading dataset feeds
                    if feed_type == 'Dataset':
                        print(f"{dataSet} : {feed_type}")
                        feed_id = metadata.get('@id')
                        if feed_id:
                            if feed_id not in excluded_feeds:
                                org, created = OpenActiveFeed.objects.update_or_create(
                                    org=feed_id,
                                    defaults={
                                        'metadata': metadata
                                    }
                                )
                        else:
                            self.stdout.write(self.style.ERROR(f'{dataSet}: No id in metadata {metadata}'))
                    else:
                        self.stdout.write(self.style.ERROR(f'{dataSet}: @type {feed_type} not supported'))

                else:
                    self.stdout.write(self.style.ERROR(f'No metadata for {dataSet}'))

