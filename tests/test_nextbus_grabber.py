import unittest
from bust import nextbus_grabber

class NextbusDatastoreTest(unittest.TestCase):
    def setUp(self):
        self.nextbus_datastore = nextbus_grabber.NextbusDatastoreFactory.generate_datastore()

    def test_agency_list_generation(self):
        test_agency_tags = ['actransit', 'jta', 'unitrans']
        for agency_tag in test_agency_tags:
            self.assertTrue(agency_tag in self.nextbus_datastore.agency_tags,
                '{0} not in {1}'.format(agency_tag, self.nextbus_datastore.agency_tags))

    def test_route_list_generation(self):
        test_routes = {
            'actransit' : '51B',
            'sf-mission-bay' : 'west',
            'sf-muni' : '38L',
        }
        for agency, route in test_routes.iteritems():
            self.assertTrue(route in self.nextbus_datastore.routes[agency],
                '{0} not in {1}'.format(route, self.nextbus_datastore.routes[agency]))

    def test_stop_list_generation(self):
        # TODO
        pass

class NextbusRequesterTest(unittest.TestCase):
    def setUp(self):
        self.nextbus_xmls = nextbus_grabber.NextbusRequester()

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
