import os
from abc import ABCMeta, abstractmethod
from bust.utils.pickle_wrapper import Serializer
from bust import nextbus_grabber, constants


class BusFileSystemDatastore(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def find_stops_near_lat_lon(self, lat, lon):
        pass

    @abstractmethod
    def get_agencies(self):
        pass

    @abstractmethod
    def get_agency_routes(self):
        pass

    @abstractmethod
    def save_data(self):
        pass

    @abstractmethod
    def load_data(self):
        pass

class NextBusDatastoreFactory(object):
    @staticmethod
    def generate_datastore():
        new_datastore = NextBusDatastore()
        new_datastore.init_data()
        return new_datastore

class NextBusDatastore(BusFileSystemDatastore):
    def __init__(self):
        self.file_root = ''
        self.file_path = ''
        self.stops = {}
        self.flat_index = []
        self.location_index = None
        self.set_filename('nextbus.data')

    def find_stops_near_lat_lon(self, lat, lon):
        # Dividing by 800 will have a max of 10 queries. When max search
        # distance is at 50 miles, 1/800 is about 100 meters/yards
        search_distance = constants.MAX_SEARCH_DISTANCE / 800
        stops_found = []
        while (not stops_found and search_distance <= constants.MAX_SEARCH_DISTANCE):
            stops_found = self.location_index.search_n_radius_square_around_coord(
                    search_distance, (lat, lon))
            search_distance *= 2
        if not stops_found:
            stops_found = self.location_index.search_n_radius_square_around_coord(
                constants.MAX_SEARCH_DISTANCE, (lat, lon))
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

    def init_data(self):
        if self._does_saved_data_exist():
            self.load_data()
            populator = \
                nextbus_grabber.NextBusDatastorePopulator(self, self.stops, self.flat_index)
            populator.populate_datastore()
        else:
            self.refresh_data()

    def save_data(self):
        with open(self.file_path, 'wb') as save_file:
            save_dump = Serializer.serialize([self.stops, self.flat_index])
            save_file.write(save_dump)

    def load_data(self):
        with open(self.file_path, 'rb') as load_file:
            saved_dump = load_file.read()
            saved_data = Serializer.deserialize(saved_dump)
            self.stops = saved_data[0]
            self.flat_index = saved_data[1]

    def refresh_data(self):
        populator = nextbus_grabber.NextBusDatastorePopulator(self)
        populator.populate_datastore()
        self.save_data()

    def set_file_root(self, file_root):
        self.file_root = file_root
        self.set_filename(self.filename)

    def set_filename(self, filename):
        self.file_path = self.file_root + filename

    def _does_saved_data_exist(self):
        return os.path.isfile(self.file_path)

