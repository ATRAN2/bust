RADIUS_SEARCH_URL = '/api/radius-search?lat=<latitude>&lon=<longitude>&distance=<distance_in_miles>'
AGENCIES_URL = '/api/agencies'
AGENCY_ROUTES_URL = '/api/agency-routes?atag=<agency_tag>'
ROUTE_STOPS_URL = '/api/route-stops?atag=<agency_tag>&rtag=<route_tag>'

# Max_search_distance corresponds to lat/lon
# distance and at 0.728 is around 50 miles
MAX_SEARCH_DISTANCE = 0.7246377
# Dividing by 800 will have a max of 10 queries. When max search
# distance is at 50 miles, 1/800 is about 100 meters/yards
MIN_SEARCH_DISTANCE = MAX_SEARCH_DISTANCE / 800
LATLON_DEGREE_TO_MILE = 69

API_HOME_MESSAGE = {
    'radius-search' : {
        'url' : RADIUS_SEARCH_URL,
        'action' : 'Searches and returns information about bus stops around ' +\
            '<latitude> and <longitude>. <distance_in_miles> is an optional ' +\
            'parameter that will set the search distance (in miles). Leaving ' +\
            'distance out will do gradually increasing radial searches until ' +\
            'least one stop entry is returned'
    },
    'agencies' : {
        'url' : AGENCIES_URL,
        'action' : 'Returns a list of all California agencies in the NextBus ' +\
            'feed with their agency_tags and agency_titles.'
    },
    'agency-routes': {
        'url' : AGENCY_ROUTES_URL,
        'action' : "Returns agency routes' route_tags given the agency_tag " +\
            'in <agency_tag>.'
    },
    'route-stops': {
        'url' : ROUTE_STOPS_URL,
        'action' : 'Returns the stops data which includes stop_tags (object key), ' +\
            'direction, lat, lon, stop_id (if available), and street_title. ' +\
            'Takes <agency_tag> and <route_tag> as required parameters.'
    },
}

