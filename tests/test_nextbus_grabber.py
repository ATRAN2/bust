import unittest
from bust import nextbus_grabber

class NextbusDatastoreTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.nextbus_datastore = nextbus_grabber.NextbusDatastoreFactory.generate_datastore()

    def test_location_rtree_generation(self):
        test_stop = {
            'stop_id' : '50444',
            'stop_title' : 'University Av & Shattuck Av',
            'agency_title' : 'AC Transit',
            'agency_tag' : 'actransit',
            'lat' : '37.8721999',
            'lon' : '-122.2687799',
            }
        search = self.nextbus_datastore \
            .find_stops_near_lat_lon(37.8721999, -122.2687799)
        self.assertTrue(test_stop in search)

class NextbusDatastorePopulatorTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.datastore_populator = nextbus_grabber.NextbusDatastorePopulator()
        self.datastore_populator.get_agencies()
        self.datastore_populator.get_routes()
        self.datastore_populator.get_stops()

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
                'title' : 'AC Transit',
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
                test_stop['actransit']['title'],
                self.datastore_populator.stops['actransit']['title'],
        )

class NextbusRequesterTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
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

if __name__ == '__main__':
    unittest.main()

class XMLAttributesValuesExtractorTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        nextbus_xmls = nextbus_grabber.NextbusRequester()
        self.test_xml = nextbus_xmls.get_route_stops('actransit', '51B')

    def test_extract_values(self):
        tag_attributes = {'route' : ['tag', 'title', 'color']}
        extractor = nextbus_grabber.XMLAttributesValuesExtractor(
            self.test_xml, tag_attributes)
        extracted_values = extractor.extract_values()
        self.assertEqual(
                {'tag' : ['51B'], 'title' : ['51B'], 'color' : ['49b869']},
                extracted_values,
        )

    def test_move_parsing_root(self):
        tag_attributes = {'stop' : ['tag', 'title', 'stopId']}
        extractor = nextbus_grabber.XMLAttributesValuesExtractor(
            self.test_xml, tag_attributes)
        move_parsing_root_down_one_level = [0]
        extractor.set_parsing_root(move_parsing_root_down_one_level)
        extracted_values = extractor.extract_values()
        self.assertIn('0306650', extracted_values['tag'])
        self.assertIn('University Av & Shattuck Av', extracted_values['title'])
        self.assertIn('50444', extracted_values['stopId'])

    def test_attribute_filters(self):
        tag_attributes = {'stop' : ['tag', 'title', 'stopId']}
        attribute_filter = {'tag' : '0306650', 'stopId' : '50444'}
        extractor = nextbus_grabber.XMLAttributesValuesExtractor(
            self.test_xml, tag_attributes)
        move_parsing_root_down_one_level = [0]
        extractor.set_parsing_root(move_parsing_root_down_one_level)
        extractor.set_attributes_filter(attribute_filter)
        extracted_values = extractor.extract_values()
        self.assertIn('University Av & Shattuck Av', extracted_values['title'])
        self.assertEqual(1, len(extracted_values['tag']))
