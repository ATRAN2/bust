import requests
from lxml import etree
from .bus_datastore import BusDatastore

class NextbusDatastoreFactory(object):
    @staticmethod
    def generate_datastore():
        new_datastore = NextbusDatastore()
        new_datastore.populate_datastore()
        return new_datastore

class NextbusDatastore(BusDatastore):
    def populate_datastore(self):
        populator = NextbusDatastorePopulator()
        self.agencies = populator.populate_agencies()
        self.routes = populator.populate_routes(self.agencies)

class NextbusDatastorePopulator(object):
    def __init__(self):
        self.nextbus_requester = NextbusRequester()

    def populate_agencies(self):
        agencies = {}
        agencies_xml = self.nextbus_requester.get_agencies()
        tag_attributes = {'agency' : ['tag', 'title']}
        california_filter = {'regionTitle' : 'California'}
        extracted_agencies = self.get_attribute_values_from_xml(
                agencies_xml, tag_attributes, attributes_filter=california_filter)
        agency_tags = extracted_agencies['tag']
        agency_titles = extracted_agencies['title']
        agencies = dict(zip(agency_tags, agency_titles))
        return agencies

    def populate_routes(self, agencies):
        routes = {}
        agency_tags = agencies.keys()
        tag_attributes = {'route' : ['tag']}
        for agency in agency_tags:
            routes_list_xml = self.nextbus_requester.get_route_list_from_agency(agency)
            agency_routes = self.get_attribute_values_from_xml(
                    routes_list_xml, tag_attributes)
            routes[agency] = agency_routes['tag']
        return routes

    def get_attribute_values_from_xml(self, xml, tag_attributes, parsing_root=[], attributes_filter={} ):
        xml_extractor = XMLAttributesValuesExtractor(xml, tag_attributes)
        xml_extractor.set_if_contains_attributes_filter(attributes_filter)
        xml_extractor.set_parsing_root(parsing_root)
        extracted_data = xml_extractor.extract_values()
        return extracted_data

class NextbusRequester(object):
    def __init__(self):
        self.NEXTBUS_API_ROOT = 'http://webservices.nextbus.com/service/publicXMLFeed?command='

    def get_agencies(self):
        api_command = 'agencyList'
        return self.get_response_xml_from_api_command(api_command)

    def get_route_list_from_agency(self, agency):
        api_command = 'routeList&a={0}'.format(agency)
        return self.get_response_xml_from_api_command(api_command)

    def get_route_stops(self, agency, route_tag):
        api_command = 'routeConfig&a={0}&r={1}'.format(agency, route_tag)
        return self.get_response_xml_from_api_command(api_command)

    def get_response_xml_from_api_command(self, api_command):
        api_url = self.NEXTBUS_API_ROOT + api_command
        response = requests.get(api_url)
        return response.content

class XMLAttributesValuesExtractor(object):
    def __init__(self, xml, tag_attributes_dict):
        self.extracted_data = {}
        self.xml_tree = etree.XML(xml)
        self.target_tag = tag_attributes_dict.keys()[0]
        self.target_attributes = tag_attributes_dict.values()[0]
        self.initialize_extracted_data_keys_as_target_attributes()
        self.parsing_root = []
        self.attributes_filter = {}

    def initialize_extracted_data_keys_as_target_attributes(self):
        for attribute in self.target_attributes:
            self.extracted_data[attribute] = []

    def set_parsing_root(self, parsing_root):
        self.parsing_root = parsing_root

    def set_if_contains_attributes_filter(self, attributes_filter):
        self.attributes_filter = attributes_filter

    def extract_values(self):
        self.move_to_parsing_root()
        for element in self.xml_tree:
            if element.tag == self.target_tag:
                self.extract_attribute_values_from_element(element)
        return self.extracted_data

    def move_to_parsing_root(self):
        while self.parsing_root:
            self.xml_tree[parsing_root[0]]
            self.parsing_root = self.parsing_root[1:]

    def extract_attribute_values_from_element(self, element):
        element_attributes = element.attrib.keys()
        for attribute in self.target_attributes:
            if attribute in element_attributes:
                self.extracted_data[attribute].append(element.attrib[attribute])

    def has_filter_attributes(self, element):
        if not self.attributes_filter:
            return True
        element_has_filter_attributes = True
        for attribute, value in self.attributes_filter.iteritems():
            if (attribute not in element.attrib) or \
                (value not in element.attrib[attribute]):
                element_has_filter_attributes = False
                break
        return element_has_filter_attributes
