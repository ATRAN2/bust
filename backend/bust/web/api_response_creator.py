from bust import constants


class APIResponseCreator(object):
    """
    Add formatting from queries to the BusDatastore to make the object
    jsonify-able.
    """

    def __init__(self, datastore):
        self._datastore = datastore

    def get_radius_search(self, lat, lon, distance=None):
        """
        Take distance as an optional argument.  When distance is None,
        search the lat lon location with a gradually increasing radius
        starting from a minimum distance until either stops are found
        or a maximum distance is reached. Define Minimum and maximum
        distance in constants.py.  When distance parameter is given,
        return the stops that are found from a search of distance
        radius.  Formatted result includes the search distance in
        miles as a key and search results in a list as values.
        """
        if not distance:
            search_results, distance = self._datastore.find_stops_near_lat_lon(lat, lon)
        else:
            distance_in_latlon = distance/constants.LATLON_DEGREE_TO_MILE
            search_results = self._datastore\
                .find_stops_n_distance_from_lat_lon(distance_in_latlon, lat, lon)
        formatted_results = {}
        if search_results:
            formatted_results = self._format_radius_search_results(search_results, distance)
        return formatted_results

    def get_agencies(self):
        """
        Get the all agency tags and agency titles.
        """
        return {'agencies' : self._datastore.get_agencies()}

    def get_agency_routes(self, agency_tag):
        """
        Given an agency tag, return all of its route_tags.
        """
        return {'agency-routes' : self._datastore.get_agency_routes(agency_tag)}

    def get_route_stops(self, agency_tag, route_tag):
        """
        Return the data for all the stops in an agency's route selected
        by agency_tag and route_tag.  Stop data includes stop tag (key),
        direction, coordinate, stop id (if available), and street title.
        """
        return {'route-stops' : self._datastore.get_route_stops(agency_tag, route_tag)}

    def _format_radius_search_results(self, radius_search_results, distance):
        formatted_results = {}
        search_distance = '{0}mi_search_square'.format(distance)
        formatted_results[search_distance] = radius_search_results
        return formatted_results

