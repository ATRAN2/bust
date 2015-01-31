import unittest
from bust import nextbus_grabber
from bust.utils import xml_extractor

class XMLAttributesValuesExtractorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        nextbus_client = nextbus_grabber.NextBusClient()
        cls.test_xml = nextbus_client._query_route_stops('actransit', '51B')

    def test_extract_values(self):
        tag_attributes = {'route' : ['tag', 'title', 'color']}
        extractor = xml_extractor.XMLAttributesValuesExtractor(
            self.test_xml, tag_attributes)
        extracted_values = extractor.extract_values()
        self.assertEqual(
                {'tag' : ['51B'], 'title' : ['51B'], 'color' : ['49b869']},
                extracted_values,
        )

    def test_move_parsing_root(self):
        tag_attributes = {'stop' : ['tag', 'title', 'stopId']}
        extractor = xml_extractor.XMLAttributesValuesExtractor(
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
        extractor = xml_extractor.XMLAttributesValuesExtractor(
            self.test_xml, tag_attributes)
        move_parsing_root_down_one_level = [0]
        extractor.set_parsing_root(move_parsing_root_down_one_level)
        extractor.set_attributes_filter(attribute_filter)
        extracted_values = extractor.extract_values()
        self.assertIn('University Av & Shattuck Av', extracted_values['title'])
        self.assertEqual(1, len(extracted_values['tag']))

class NextBusXMLExtractorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        nextbus_client = nextbus_grabber.NextBusClient()
        cls.test_xml = nextbus_client._query_route_stops('actransit', '51B')

    def test_get_stop_direction_data(self):
        stop_direction_data = \
            xml_extractor.NextBusXMLExtractor.get_stop_direction_data(self.test_xml)
        self.assertEqual('North', stop_direction_data['0306650']['direction_name'])
        self.assertEqual('To Berkeley Marina', stop_direction_data['0306650']['direction'])

if __name__ == '__main__':
    unittest.main()
