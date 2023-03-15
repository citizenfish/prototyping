from django.core.management.base import BaseCommand, CommandError
from .osdata import OSdata
class Command(BaseCommand):
    help = 'Load OS Opennames data'

    def add_arguments(self,parser):
        parser.add_argument('--gpkg', default='', type=str)
    def handle(self, *args, **options):

        # Step 1 download the required data from OS, only GeoPackage supported at present
        downloader = OSdata(product='OpenNames', format='GeoPackage')

        # For testing we can bypass download
        if options['gpkg'] == '':
            file = downloader.download()
            self.stdout.write(self.style.SUCCESS(f'Processing {file["filename"]}'))
        else:
            downloader.filename = options['gpkg']

        # Step 2 import using OGR2OGR
        result = downloader.ogr_import(model_name='geocoder_opennames', layer_name='named_place')
        self.stdout.write(self.style.SUCCESS('Ran the OS Opennames Loader'))

