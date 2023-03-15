from django.contrib.gis.geos import Point
from geocoder.models import Opennames

class OpennamesGeocoder:
    @staticmethod
    def geocode(postcode):
        try:
            # Query the OpenName model using the provided postcode and local_type constraint
            postcode = postcode.replace(' ','')
            formatted_postcode = " ".join([postcode[:-3], postcode[-3:]]).upper()

            print(postcode)
            print(formatted_postcode)
            result = Opennames.objects.get(name1=formatted_postcode, local_type='Postcode')

            # Return the coordinates as a tuple
            return result.geom.coords
        except Opennames.DoesNotExist:
            print(f'[{formatted_postcode}] Does not exist')
            # If no matching result is found, return None
            return None
