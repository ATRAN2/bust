import unittest
from bust import nextbus_grabber, bus_datastore

# NextBusDatastorePopulatorTest takes some time to run as
# it must query the NextBus API a lot.
class NextBusDatastorePopulatorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.datastore_populator = \
            nextbus_grabber.NextBusDatastorePopulator(bus_datastore.NextBusDatastore)
        cls.datastore_populator._get_agencies()
        cls.datastore_populator._get_routes()
        cls.datastore_populator._get_stops()
        cls.datastore_populator._parse_stops_data_into_location_index()

    def test_get_agencies(self):
        test_agencies = {
            'actransit' : 'AC Transit',
            'glendale' : 'Glendale Beeline',
            'unitrans' : 'Unitrans ASUCD/City of Davis',
        }
        datastore_agencies = self.datastore_populator._agencies
        for agency_tag, agency_title in test_agencies.iteritems():
            self.assertTrue(datastore_agencies[agency_tag] == agency_title,
                '{{{0} : {1}}}not in {2}'.format(
                    agency_tag, agency_title, datastore_agencies))

    def test_get_routes(self):
        test_routes = {
            'actransit' : '51B',
            'sf-mission-bay' : 'west',
            'sf-muni' : '38L',
        }
        datastore_routes = self.datastore_populator._routes
        for agency, route in test_routes.iteritems():
            self.assertTrue(route in datastore_routes[agency],
                '{0} not in {1}'.format(route, datastore_routes[agency]))

    def test_get_stops(self):
        test_stop = {
            'actransit' : {
                'agency_title' : 'AC Transit',
                'route' : {
                    '51B' : {
                        '0302030' : {
                            'title' : 'Durant Av & Telegraph Av',
                            'lat' : '37.8677199',
                            'lon' : '-122.2592',
                            'stopId' : '55556',
                            'direction' : 'To Rockridge BART',
                            'direction_name' : 'South',
                        }
                    }
                }
            }
        }
        datastore_stops = self.datastore_populator._stops
        self.assertEqual(
                test_stop['actransit']['route']['51B']['0302030'],
                datastore_stops['actransit']['route']['51B']['0302030'],
        )
        self.assertEqual(
                test_stop['actransit']['agency_title'],
                datastore_stops['actransit']['agency_title'],
        )

    def test_parse_stops_data_into_location_index(self):
        test_location = {
            'stop_id' : '50444',
            'route_tag' : '51B',
            'stop_tag' : '0306650',
            'street_title' : 'University Av & Shattuck Av',
            'agency_title' : 'AC Transit',
            'agency_tag' : 'actransit',
            'lat' : '37.8721999',
            'lon' : '-122.2687799',
            'direction' : 'To Berkeley Marina',
            'direction_name' : 'North'
        }
        location_index = self.datastore_populator._location_index
        search = location_index.search_in_range((37.8715, -122.269, 37.8725, -122.268))
        self.assertTrue(test_location in search)

class NextBusClientTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nextbus_client = nextbus_grabber.NextBusClient()

    def test_query_nextbus_agencies(self):
        nextbus_agencies_xml = self.nextbus_client._query_agencies()
        self.assertIn(
                '<agency tag=',
                nextbus_agencies_xml,
        )

    def test_query_route_list_from_agency(self):
        actransit_routes_xml = self.nextbus_client._query_route_list_from_agency('actransit')
        self.assertIn(
                '<route tag="',
                actransit_routes_xml,
        )

    def test_query_route_stops(self):
        route_51b_xml = self.nextbus_client._query_route_stops('actransit', '51B')
        self.assertIn(
                '<stop tag="',
                route_51b_xml,
        )

if __name__ == '__main__':
    unittest.main()
