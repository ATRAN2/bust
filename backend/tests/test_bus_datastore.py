import unittest
from bust import bus_datastore, constants

# Will be slow the first time since it has to query
# the NextBus API.  Afterwards it'll load results from
# disk which is a lot faster.
class NextBusDatastoreTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nextbus_datastore = bus_datastore.NextBusDatastoreFactory.generate_datastore()

    def test_location_rtree_generation(self):
        test_stop = {
            'stop_id' : '50444',
            'route_tag' : '51B',
            'stop_tag' : '0306650',
            'street_title' : 'University Av & Shattuck Av',
            'agency_title' : 'AC Transit',
            'agency_tag' : 'actransit',
            'lat' : '37.8721999',
            'lon' : '-122.2687799',
            'direction' : 'To Berkeley Marina',
            'direction_name' : 'North',
        }
        search_result, distance = self.nextbus_datastore \
            .find_stops_near_lat_lon(37.8721999, -122.2687799)
        self.assertTrue(test_stop in search_result)
        self.assertTrue(distance >= constants.MIN_SEARCH_DISTANCE)
        self.assertTrue(distance <= constants.MAX_SEARCH_DISTANCE)


if __name__ == '__main__':
    unittest.main()
