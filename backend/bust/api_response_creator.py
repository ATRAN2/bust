from bust import nextbus_grabber

class APIResponseURLs(object):
    def __init__(self):
        self.radius_search_url = '/api/radius-search?lat=<latitude>&lon=<longitude>'
        self.agencies_url = '/api/agencies'
        self.agency_routes_url= '/api/agency-routes?atag=<agency_tag>'

class APIResponseCreator(object):
    def __init__(self, datastore):
        self.datastore = datastore

    def create_radius_search(self, lat, lon):
        search_results = self.datastore.find_stops_near_lat_lon(lat, lon)
        formatted_results = {}
        if search_results:
            formatted_results = self.format_radius_search_results(search_results)
        return formatted_results

    def format_radius_search_results(self, radius_search_results):
        formatted_results = {}
        for result in radius_search_results:
            if 'stop_id' in result:
                stop_id = result.pop('stop_id')
                formatted_results[stop_id] = result
            else:
                formatted_results['N/A'] = result
        return formatted_results

