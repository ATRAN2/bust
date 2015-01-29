from abc import ABCMeta, abstractmethod
from bust import pickle_wrapper as pickler
from bust import rtree_wrapper as rtree

class BusDatastore(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.stops = None
        self.location_rtree = None
        self.FILE_ROOT = './bust/bus_data/'
        self.set_filename('bus.data')
    
    @abstractmethod
    def find_stops_near_lat_lon(self, lat, lon):
        pass

    @abstractmethod
    def save_data_to_disk(self):
        pass

    @abstractmethod
    def load_data_from_disk(self):
        pass

    def set_filename(self, filename):
        self.file_path = self.FILE_ROOT + filename


