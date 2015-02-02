RADIUS_SEARCH_URL = '/api/radius-search?lat=<latitude>&lon=<longitude>&distance=<distance_in_miles>'
AGENCIES_URL = '/api/agencies'
AGENCY_ROUTES_URL = '/api/agency-routes?atag=<agency_tag>'

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
        'action' : 'Searches and returns information about bus stops around <latitude> and <longitude>.' + \
            ' <distance_in_miles> is an optional parameter that will set the search distance (in miles).'},
    'agencies' : {
        'url' : AGENCIES_URL,
        'action' : 'Returns a list of all California agencies in the Nextbus feed with their agency_tags and agency_titles'},
    'agency_routes': {
        'url' : AGENCY_ROUTES_URL,
        'action' : 'Returns agency routes and route_tags'}
}

