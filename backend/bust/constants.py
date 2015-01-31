RADIUS_SEARCH_URL = '/api/radius-search?lat=<latitude>&lon=<longitude>'
AGENCIES_URL = '/api/agencies'
AGENCY_ROUTES_URL = '/api/agency-routes?atag=<agency_tag>'

# Max_search_distance corresponds to lat/lon
# distance and at 0.728 is around 50 miles
MAX_SEARCH_DISTANCE = 0.728

API_HOME_MESSAGE = {
        'radius-search' : {
            'url' : RADIUS_SEARCH_URL,
            'action' : 'Searches and returns information about bus stops around <latitude> and <longitude>'},
        'agencies' : {
            'url' : AGENCIES_URL,
            'action' : 'Returns a list of all California agencies in the Nextbus feed with their agency_tags and agency_titles'},
        'agency_routes': {
            'url' : AGENCY_ROUTES_URL,
            'action' : 'Returns agency routes and route_tags'}
    }

