from bust import constants

class APIResponseCreator(object):
    def __init__(self, datastore):
        self._datastore = datastore

    def get_radius_search(self, lat, lon, distance=None):
        if not distance:
            search_results, distance = self._datastore.find_stops_near_lat_lon(lat, lon)
        else:
            distance_in_latlon = distance/constants.LATLON_DEGREE_TO_MILE
            search_results = self._datastore\
                .find_stops_n_distance_from_lat_lon(distance, lat, lon)
        formatted_results = {}
        if search_results:
            formatted_results = self._format_radius_search_results(search_results, distance)
        return formatted_results

    def get_agencies(self):
        return {'agencies' : self._datastore.get_agencies()}

    def get_agency_routes(self, agency_tag):
        return {'agency-routes' : self._datastore.get_agency_routes(agency_tag)}

    def _format_radius_search_results(self, radius_search_results, distance):
        formatted_results = {}
        search_distance = '{0}mi_search_square'.format(distance)
        formatted_results[search_distance] = radius_search_results
        return formatted_results

