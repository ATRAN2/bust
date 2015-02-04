import unittest

from bust.components import nextbus_client


class NextBusClientTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nextbus_client = nextbus_client.NextBusClient()

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
