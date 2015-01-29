import unittest
from bust import nextbus_grabber

@unittest.skip('Takes a while')
class NextbusDatastoreTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nextbus_datastore = nextbus_grabber.NextbusDatastoreFactory.generate_datastore()

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
            }
        search = self.nextbus_datastore \
            .find_stops_near_lat_lon(37.8721999, -122.2687799)
        self.assertTrue(test_stop in search)

# NextbusDatastorePopulatorTest takes some time to run as
# it must query the Nextbus API a lot.
@unittest.skip('Takes a long time')
class NextbusDatastorePopulatorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.datastore_populator = nextbus_grabber.NextbusDatastorePopulator()
        cls.datastore_populator.get_agencies()
        cls.datastore_populator.get_routes()
        cls.datastore_populator.get_stops()

    def test_get_agencies(self):
        test_agencies = {
            'actransit' : 'AC Transit',
            'glendale' : 'Glendale Beeline',
            'unitrans' : 'Unitrans ASUCD/City of Davis',
        }
        for agency_tag, agency_title in test_agencies.iteritems():
            self.assertTrue(self.datastore_populator.agencies[agency_tag] == agency_title,
                '{{{0} : {1}}}not in {2}'.format(
                    agency_tag, agency_title, self.datastore_populator.agencies))

    def test_get_routes(self):
        test_routes = {
            'actransit' : '51B',
            'sf-mission-bay' : 'west',
            'sf-muni' : '38L',
        }
        for agency, route in test_routes.iteritems():
            self.assertTrue(route in self.datastore_populator.routes[agency],
                '{0} not in {1}'.format(route, self.datastore_populator.routes[agency]))

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
                            'stopId' : '55556'
                        }
                    }
                }
            }
        }
        self.assertEqual(
                test_stop['actransit']['route']['51B']['0302030'],
                self.datastore_populator.stops['actransit']['route']['51B']['0302030'],
        )
        self.assertEqual(
                test_stop['actransit']['agency_title'],
                self.datastore_populator.stops['actransit']['agency_title'],
        )

    def test_parse_stops_data_into_location_rtree(self):
        location_rtree = self.datastore_populator.parse_stops_data_into_location_rtree()
        test_stop = {
            'stop_id' : '50444',
            'route_tag' : '51B',
            'stop_tag' : '0306650',
            'street_title' : 'University Av & Shattuck Av',
            'agency_title' : 'AC Transit',
            'agency_tag' : 'actransit',
            'lat' : '37.8721999',
            'lon' : '-122.2687799',
            }
        search = location_rtree.search_in_range((37.8715, -122.269, 37.8725, -122.268))
        self.assertTrue(test_stop in search)

class NextbusRequesterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nextbus_xmls = nextbus_grabber.NextbusRequester()

    def test_get_nextbus_agencies(self):
        nextbus_agencies_xml = self.nextbus_xmls.get_agencies()
        self.assertIn(
                '<agency tag=',
                nextbus_agencies_xml,
        )

    def test_get_route_list_from_agency(self):
        actransit_routes_xml = self.nextbus_xmls.get_route_list_from_agency('actransit')
        self.assertIn(
                '<route tag="',
                actransit_routes_xml,
        )

    def test_get_route_stops(self):
        route_51b_xml = self.nextbus_xmls.get_route_stops('actransit', '51B')
        self.assertIn(
                '<stop tag="',
                route_51b_xml,
        )

if __name__ == '__main__':
    unittest.main()
