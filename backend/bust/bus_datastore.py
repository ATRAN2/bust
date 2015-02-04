from abc import ABCMeta, abstractmethod

from bust.utils.serializer import Serializer
from bust.components import nextbus_grabber
from bust import constants, config


class BusDatastore(object):
    """
    BusDatastore interface that defines the methods that need to be 
    implemented in order to work with the API.
    TODO: Add the 511 data to use as a Transit511BusDatastore
    """

    __metaclass__ = ABCMeta
    @abstractmethod
    def find_stops_near_lat_lon(self, lat, lon):
        """
        Given a coordinate lat lon, find nearby bus stops.  The distance
        of search should gradually increase until results are found.
        """
        pass

    @abstractmethod
    def find_stops_n_distance_from_lat_lon(self, distance, lat, lon):
        """
        Given a coordinate lat lon, find nearby bus stops within the
        specified distance.
        """
        pass

    @abstractmethod
    def get_agencies(self):
        """ Return bus agency titles and/or tags """
        pass

    @abstractmethod
    def get_agency_routes(self):
        """ Return routes associated with an agency """
        pass

class NextBusDatastoreFactory(object):
    """
    Create a NextBusDatastore instance. Load data created from script
    build_datastore.py.  Script should be run prior to initial start
    """

    @staticmethod
    def generate_datastore():
        """ Method to create a datastore by loading from file  """
        new_datastore = NextBusDatastore()
        datastore_populator = nextbus_grabber.NextBusDatastorePopulator(new_datastore)
        datastore_populator.populate_from_file()
        return new_datastore

class NextBusDatastore(BusDatastore):
    """
    Datastore pertaining to data from the NextBus API.  Contains a map
    storing all the static data for each stop and a spatial index to 
    search for stops based on location.
    """

    def __init__(self):
        self.stops = {}
        self.flat_index = []
        self.location_index = None
        self.file_path = config.NEXTBUS_FILE_PATH

    def find_stops_near_lat_lon(self, lat, lon):
        """
        Given lat lon, find nearby bus stops and returns as soon as at least
        one stop is found.  Search starts from a minimum distance until a
        max distance given in constants.py.  Return stop data as well as
        distance searched.
        """
        search_distance = constants.MIN_SEARCH_DISTANCE
        stops_found = []
        while (not stops_found and search_distance <= constants.MAX_SEARCH_DISTANCE):
            stops_found = self.location_index.search_n_distance_around_coord(
                search_distance, (lat, lon))
            search_distance *= 2
        search_distance /= 2
        if not stops_found:
            stops_found = self.location_index.search_n_distance_around_coord(
                constants.MAX_SEARCH_DISTANCE, (lat, lon))
            search_distance = constants.MAX_SEARCH_DISTANCE
        stops_distance = [stops_found, search_distance*constants.LATLON_DEGREE_TO_MILE]
        return stops_distance

    def find_stops_n_distance_from_lat_lon(self, n_distance, lat, lon):
        """ Return stops data for stops  n_distance around lat lon """
        stops_found = self.location_index\
                .search_n_distance_around_coord(n_distance, (lat, lon))
        return stops_found

    def get_agencies(self):
        """ Return agency tags and corresponding agency titles """
        agencies = {}
        for agency_tag, agency_data in self.stops.iteritems():
            agencies[agency_tag] = agency_data['agency_title']
        return agencies

    def get_agency_routes(self, agency):
        """ Return routes associated with a bus agency """
        route_data = self.stops[agency]['route']
        route_tags = route_data.keys()
        agency_routes = {agency : route_tags}
        return agency_routes

    def get_route_stops(self, agency, route):
        """ Return the stops stops data from an agency's route """
        stops_data = self.stops[agency]['route'][route]
        return stops_data

    def save_data(self):
        """ Save data disk as given by the path in config.py """
        with open(self.file_path, 'wb') as save_file:
            save_dump = Serializer.serialize(self.stops)
            save_file.write(save_dump)

    def load_data(self):
        """ Load data in disk as given by the path in config.py """
        with open(self.file_path, 'rb') as load_file:
            saved_dump = load_file.read()
            saved_data = Serializer.deserialize(saved_dump)
            self.stops = saved_data
