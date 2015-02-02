from abc import ABCMeta, abstractmethod
from bust.utils.pickle_wrapper import Serializer
from bust import nextbus_grabber, constants, config


class BusDatastore(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def find_stops_near_lat_lon(self, lat, lon):
        pass

    @abstractmethod
    def find_stops_n_distance_from_lat_lon(self, distance, lat, lon):
        pass

    @abstractmethod
    def get_agencies(self):
        pass

    @abstractmethod
    def get_agency_routes(self):
        pass

class NextBusDatastoreFactory(object):
    @staticmethod
    def generate_datastore():
        new_datastore = NextBusDatastore()
        datastore_populator = nextbus_grabber.NextBusDatastorePopulator(new_datastore)
        datastore_populator.populate_from_file()
        return new_datastore

class ScriptToCreateDatastoreFromWebToFile(object):
    def run(self):
        new_datastore = NextBusDatastore()
        datastore_populator = nextbus_grabber.NextBusDatastorePopulator(new_datastore)
        datastore_populator.populate_from_web()
        new_datastore.save_data()

class NextBusDatastore(BusDatastore):
    def __init__(self):
        self.stops = {}
        self.flat_index = []
        self.location_index = None
        self.file_path = config.SAVE_PATH

    def find_stops_near_lat_lon(self, lat, lon):
        search_distance = constants.MIN_SEARCH_DISTANCE
        stops_found = []
        while (not stops_found and search_distance <= constants.MAX_SEARCH_DISTANCE):
            stops_found = self.location_index.search_n_size_square_around_coord(
                search_distance, (lat, lon))
            search_distance *= 2
        search_distance /= 2
        if not stops_found:
            stops_found = self.location_index.search_n_size_square_around_coord(
                constants.MAX_SEARCH_DISTANCE, (lat, lon))
            search_distance = constants.MAX_SEARCH_DISTANCE
        stops_distance = [stops_found, search_distance*constants.LATLON_DEGREE_TO_MILE]
        return stops_distance

    def find_stops_n_distance_from_lat_lon(self, n_distance, lat, lon):
        stops_found = self.location_index\
                .search_n_size_square_around_coord(n_distance, (lat, lon))
        return stops_found

    def get_agencies(self):
        agencies = {}
        for agency_tag, agency_data in self.stops.iteritems():
            agencies[agency_tag] = agency_data['agency_title']
        return agencies

    def get_agency_routes(self, agency):
        route_data = self.stops[agency]['route']
        route_tags = route_data.keys()
        agency_routes = {agency : route_tags}
        return agency_routes

    def save_data(self):
        with open(self.file_path, 'wb') as save_file:
            save_dump = Serializer.serialize([self.stops])
            save_file.write(save_dump)

    def load_data(self):
        with open(self.file_path, 'rb') as load_file:
            saved_dump = load_file.read()
            saved_data = Serializer.deserialize(saved_dump)
            self.stops = saved_data[0]

