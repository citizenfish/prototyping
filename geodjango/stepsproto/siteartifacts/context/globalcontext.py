from django.conf import settings

def site_settings(request):
    ## TODO retrieve from database
    return {
        'site_title' : 'Brixham Steps',
        'default_map_lon': settings.DEFAULT_MAP_LON,
        'default_map_lat': settings.DEFAULT_MAP_LAT
    }