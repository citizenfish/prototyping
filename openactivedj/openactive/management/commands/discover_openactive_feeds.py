from openactive.common.util.json import get_json, get_json_ld
from django.core.management.base import BaseCommand, CommandError
from openactive.models import Parameter, Feed, FeedDistribution


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
        parser.add_argument(
            '--reload',
            action='store_true',
            help='Delete all existing data and reload',
            required=False,
            default=False
        )
        parser.add_argument(
            '--reload_no_warnings',
            action='store_true',
            help='Delete all existing data and reload',
            required=False,
            default=False
        )

        parser.add_argument(
            '--use_default_url',
            action='store_true',
            help='Use default url',
            required=False,
            default=False
        )
    def handle(self, *args, **options):

        reload = options.get('reload','reload_no_warnings')
        if reload:
            self.truncate_all(options['reload_no_warnings'])

        self.stdout.write(self.style.NOTICE('Discovering OpenActive Feeds'))

        # Can exclude organisations if we want
        excluded_feeds = options.get('excluded_feeds', '')
        excluded_feeds = excluded_feeds.split(',') if excluded_feeds else []

        # We need a catalog url to work out from
        url = options.get('openactive_discovery_url')
        if not url:
            try:
                url = Parameter.objects.get(name='openactive_discovery_url').value
            except  Parameter.DoesNotExist:
                if not options['use_default_url']:
                    s = input(f'openactive_discovery_url not set, use default url {self.url} [y/N]')
                    if s[0].lower() != 'y':
                        raise CommandError('openactive_discovery_url has not been defined in parameters or command line')

                url = self.url

        # First we pull our list of catalogues
        catalogues = get_json(url, 'hasPart')
        if not catalogues:
            raise CommandError(f'Nothing found at {url} {catalogues}')

        for hasPart in catalogues:

            # First we must get a list of providers
            data_catalogues = get_json(hasPart, 'dataset')

            for dataSet in data_catalogues:
                # We retrieve the metadata for each catalogue this is an embedded JSON+LD structure in a HTML page :-(
                metadata = get_json_ld(dataSet)

                if metadata:
                    feed_type = metadata.get('@type')
                    # We are only loading dataset feeds
                    if feed_type == 'Dataset':
                        org = metadata.get('@id')
                        self.stdout.write(self.style.NOTICE(f'Loading Dataset from {org}'))
                        if org:
                            if org not in excluded_feeds:
                                f_org, created = Feed.objects.update_or_create(
                                    org=org,
                                    defaults={
                                        'metadata': metadata
                                    }
                                )

                                self.stdout.write(self.style.NOTICE(f'Added {org}')) if created else self.stdout.write(
                                    self.style.NOTICE(f' Update {org}'))

                            # Now add the distributions for each feed
                            for distribution in metadata.get('distribution'):
                                distribution_type = self.additional_type(distribution)
                                self.stdout.write(self.style.NOTICE(f'Loading Distribution type {distribution_type}'))

                                if distribution.get('@type') == 'DataDownload':

                                    d_org, created = FeedDistribution.objects.update_or_create(
                                        dist_org=f_org,
                                        additionaltype=distribution_type,
                                        defaults={
                                            'contenturl': distribution.get('contentUrl'),
                                            'encoding': distribution.get('encodingFormat'),
                                            'dist_name': distribution.get('name', ''),
                                            'metadata': distribution,
                                            'additionaltype': distribution_type
                                        }
                                    )
                                self.stdout.write(self.style.NOTICE(f'Added {org}')) if created else self.stdout.write(
                                    self.style.NOTICE(f' Update {org}'))

                        else:
                            self.stderr.write(self.style.ERROR(f'{dataSet}: No id in metadata {metadata}'))
                    else:
                        self.stderr.write(self.style.ERROR(f'{dataSet}: @type {feed_type} not supported'))

                else:
                    self.stderr.write(self.style.ERROR(f'No metadata for {dataSet}'))

    def truncate_all(self, warnings):
        if warnings:
            s = input('Delete ALL discovered feeds [y/N]')
            if s[0].lower() != 'y':
                return

        self.stdout.write(self.style.WARNING('*** Deleting all discovered feeds ***'))
        Feed.objects.all().delete()


    def additional_type(self,distribution):

        a_type=distribution.get('additionalType')
        if a_type:
            return a_type

        self.stderr.write(self.style.WARNING('additionalType not found retrieving sample record'))

        try:
            sample = get_json(distribution.get('contentUrl'))
            kind = sample.get('items')[0]['kind']
            self.stderr.write(self.style.ERROR(f'Found {kind}'))
            return f'https://openactive.io/{kind}'

        except Exception:
            return None
