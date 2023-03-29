from openactive.models import Course, Event, CourseInstance, FacilityUse, League, OnDemandEvent, IndividualFacilityUse, \
    Session, SessionSeries, ScheduledSession
from openactive.common.util.map import insert_blocks

GLOBALS = {
    'GEOCODER': {
        'longitude': {'paths': ['data.location.geo.longitude', 'data.VenueLongitude'], 'type': 'float'},
        'latitude': {'paths': ['data.location.geo.latitude', 'data.VenueLatitude'], 'type': 'float'},
        'gridref': {'paths': ['data.location.grid_ref']},
        'locationpostcode': {'paths': ['data.location.address.postalCode', 'data.location.postcode',
                                       'data.organizer.address.postalCode']},
        'locality': {'paths': ['data.location.address.addressLocality', 'data.organizer.address.addressLocality',
                               'data.location.address.streetAddress', 'data.location.address.addressRegion',
                               'data.location.address']},

    },
    'SYSTEM': {
        'oa_id': {'paths': ['id']},
        'oa_org': f'{{org}}',
        'eventurl': {'paths': ['data.url', 'data.session_url', 'data.LeagueURL', 'data.beta:virtualLocation.url'], 'default': ''},
        'license': f'{{license}}',
        'modified': {'paths': ['modified'], 'type': 'str'},
        'rawdata': '*',
        'state': {'paths': ['state'], 'default': 'updated'},
        'online': {'paths': ['data.beta:virtualLocation.url'], 'type': 'exists'}
    },
    'CONTACT': {
        'organisername': {'paths': ['data.organizer.name', 'data.VenueName'], 'default': ''},
        'contactphone': {'paths': ['data.organizer.telephone', 'data.location.telephone', 'data.contact.phone',
                                   'data.beta:contactPoint.telephone'],
                         'default': ''},
        'contactemail': {'paths': ['data.beta:contactPoint.email']},
        'locationname': {'paths': ['data.location.name', 'data.VenueAddress', 'data.location.address.postalCode',
                                   'data.organizer.address.postalCode', 'data.beta:virtualLocation.name'],
                         'default': ''},
        'organiserurl': {'paths': ['data.organizer.url']},

        'locationaddress1': {'paths': ['data.location.address.streetAddress', 'data.location.address'], 'type': 'str'},
        'locationaddress2': {'paths': ['data.location.address.addressLocality'], 'type': 'str'},
        'locationaddress3': {'paths': ['data.location.address.addressRegion'], 'type': 'str'},
        'locationaddress4': {'paths': ['data.location.address.postalCode'], 'type': 'str'},
        'locationaddress5': {'paths': ['data.location.address.Country'], 'type': 'str'},
    },
    'COURSE': {
        'title': {'paths': ['data.instanceOfCourse.name', 'data.name'], 'default':''},
        'description': {'paths': ['data.instanceOfCourse.description', 'data.description'], 'default':''},
        'sourcetags': {'paths': ['data.instanceOfCourse.category','$..["prefLabel"]'], 'type': 'array', 'default': ['course']},
        'agemin': {'paths': ['data.instanceOfCourse.ageRange.minValue'], 'type': 'int', 'default': 0},
        'agemax': {'paths': ['data.instanceOfCourse.ageRange.maxValue'], 'type': 'int', 'default': 0},
        'images': {'paths': ["$.data.image[?(@['@type']=='ImageObject')].url"], 'type': 'array', 'default': []}
    },
    'EVENT': {
        'title': {'paths': ['data.name', 'data.superEvent.name', 'data.beta:sportsActivityLocation.name'], 'default':''},
        'description': {
            'paths': ['data.description', 'data.superEvent.description', 'data.provider.name', 'data.location.name', 'data.beta:sportsActivityLocation.type'], 'default':''},
        'sourcetags': {'paths': ['$..["prefLabel"]', 'data.activity', 'data.activities'], 'type': 'array',
                       'default': ['event']},
        # TODO British Orienteering case handling
        'agemin': {'paths': ['data.ageRange.minValue'], 'type': 'int', 'default': 0},
        'agemax': {'paths': ['data.ageRange.maxValue'], 'type': 'int', 'default': 0},
        'images': {'paths': ["$.data.image[?(@['@type']=='ImageObject')].url"], 'type': 'array', 'default': []}
    }
    ,
    'DATE': {
        'eventdate': {'paths': ['data.startDate', 'data.start_date', 'data.SeasonStart', '$.[*]..["startDate"]'],
                      'type': 'datetime'},
        'eventtime': {'paths': ['$.[*]..["startTime"]', '$.[*]..["startDate"]'], 'type': 'time'},

        'eventdatestart': {'paths': ['data.startDate', 'data.start_date', 'data.SeasonStart', '$.[*]..["startDate"]'],
                           'type': 'datetime'},
        'eventdateend': {'paths': ['data.endDate', 'data.end_date', 'data.SeasonEnd', '$.[*]..["endDate"]'],
                         'type': 'datetime'}
    }
}

MODEL_MAP = {
    'event': {
        'SYSTEM': 'default',
        'GEOCODER': 'default',
        'CONTACT': 'default',
        'EVENT': 'default',
        'DATE': 'default',

        'model': Event
    },
    'course': {

        'SYSTEM': 'default',
        'GEOCODER': 'default',
        'CONTACT': 'default',
        'COURSE': 'default',
        'DATE': 'default',
        'model': Course
    },
    'courseinstance': {
        'SYSTEM': 'default',
        'GEOCODER': 'default',
        'CONTACT': 'default',
        'COURSE': 'default',
        'DATE': 'default',
        'model': CourseInstance
    },
    'facilityuse': {
        'SYSTEM': 'default',
        'GEOCODER': 'default',
        'CONTACT': 'default',
        'EVENT': 'default',
        'DATE': 'default',
        'model': FacilityUse
    },
    'individualfacilityuse': {
        'SYSTEM': 'default',
        'GEOCODER': 'default',
        'CONTACT': 'default',
        'EVENT': 'default',
        'DATE': 'default',
        'model': IndividualFacilityUse
    },
    'session': {
        'SYSTEM': 'default',
        'GEOCODER': 'default',
        'CONTACT': 'default',
        'EVENT': 'default',
        'DATE': 'default',

        'model': Session
    },
    'sessionseries': {
        'SYSTEM': 'default',
        'GEOCODER': 'default',
        'CONTACT': 'default',
        'EVENT': 'default',
        'DATE': 'default',

        'model': SessionSeries
    },
    'scheduledsession': {
        'SYSTEM': 'default',
        'GEOCODER': 'default',
        'CONTACT': 'default',
        'EVENT': 'default',
        'DATE': 'default',

        'model': ScheduledSession
    },
    'league': {
        'SYSTEM': 'default',
        'GEOCODER': 'default',
        'CONTACT': 'default',
        'DATE': 'default',

        'title': {'paths': ['data.LeagueName']},
        'description': {'paths': ['data.LeagueTypeDetails']},

        'sourcetags': {'paths': ['data.SportName'], 'type': 'array', 'default': ['league']},
        'images': {'paths': ['data.ImageURL'], 'type': 'array', 'default': []},
        'agemin': 16,
        'agemax': 100,
        'model': League
    },
    'ondemandevent': {

        'SYSTEM': 'default',
        'GEOCODER': 'default',
        'CONTACT': 'default',
        'EVENT': 'default',
        'DATE': 'default',
        'online': True,
        'model': OnDemandEvent
    }
}

# Merge globals in
insert_blocks(MODEL_MAP, GLOBALS)
