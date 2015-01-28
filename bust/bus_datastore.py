from abc import ABCMeta, abstractmethod

class BusDatastore(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.stops = None
        self.location_rtree = None
    
    @abstractmethod
    def find_stops_near_lat_lon(self, lat, lon):
        pass
