class APIResponseCreator(object):
    def __init__(self, datastore):
        self._datastore = datastore

    def get_radius_search(self, lat, lon):
        search_results = self._datastore.find_stops_near_lat_lon(lat, lon)
        formatted_results = {}
        if search_results:
            formatted_results = self._format_radius_search_results(search_results)
        return formatted_results

    def get_agencies(self):
        return self._datastore.get_agencies()

    def get_agency_routes(self, agency_tag):
        return self._datastore.get_agency_routes(agency_tag)

    def _format_radius_search_results(self, radius_search_results):
        formatted_results = {}
        for result in radius_search_results:
            if 'stop_tag' in result:
                stop_tag = result.pop('stop_tag')
                formatted_results[stop_tag] = result
            else:
                formatted_results['N/A'] = result
        return formatted_results

