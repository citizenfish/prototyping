from django.contrib.gis.geos import Point
from geocoder.models import Opennames
import pyproj


class OpennamesGeocoder:
    @staticmethod
    def geocode(postcode):
        try:
            # Query the OpenName model using the provided postcode and local_type constraint
            postcode = postcode.replace(' ', '')
            formatted_postcode = " ".join([postcode[:-3], postcode[-3:]]).upper()
            result = Opennames.objects.get(name1=formatted_postcode, local_type='Postcode')

            # Return the coordinates as a tuple
            return result.geom

        except Opennames.DoesNotExist:

            # If no matching result is found, return None
            return None


class GridRefGeocoder:

    @staticmethod
    def geocode(gridref, crs='EPSG:4326'):
        # Convert UK grid reference to easting and northing coordinates
        letters = 'ABCDEFGHJKLMNOPQRSTUVWXYZ'
        easting = 0
        northing = 0
        gridref = gridref.upper()
        for i in range(len(gridref)):
            if gridref[i] in letters:
                easting = easting * 26 + letters.index(gridref[i]) + 1
                northing = northing * 26 + letters.index(gridref[i + 1]) + 1
                break
        easting += int(gridref[i + 2:i + 5]) * 100
        northing += int(gridref[i + 5:i + 8]) * 100

        # Create a GeoDjango point geometry object
        point = Point(easting, northing, srid=27700)
        point.transform(crs)

        return point


class CoordinateGeocoder:

    @staticmethod
    def geocoder(x, y, in_crs='EPSG:4326', out_crs='EPSG:4326'):
        # need a numeric code for CRS to set point srid
        in_crs_code = pyproj.CRS(in_crs).to_epsg()

        # Create a GeoDjango point geometry in the output CRS
        point = Point(x, y, srid=in_crs)
        point.srid = in_crs_code
        point.transform(out_crs)

        return point
