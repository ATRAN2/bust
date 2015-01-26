import requests
from lxml import etree
from .bus_datastore import BusDatastore

class NextbusDatastoreFactory(object):
    @staticmethod
    def generate_datastore():
        new_datastore = NextbusDatastore()
        new_datastore.populate()
        return new_datastore

class NextbusDatastore(BusDatastore):
    def populate(self):
        populator = NextbusDatastorePopulator()
        self.agency_tags = populator.populate_agencies()
        self.routes = populator.populate_routes(self.agency_tags)

class NextbusDatastorePopulator(object):
    def __init__(self):
        self.nextbus_requester = NextbusRequester()

    def populate_agencies(self):
        agencies_xml = self.nextbus_requester.get_agencies()
        tag_attributes = {'agency' : ['tag']}
        extracted_agencies = self.get_attribute_values_from_xml(
                agencies_xml, tag_attributes)
        agency_tags = extracted_agencies['tag']
        return agency_tags

    def populate_routes(self, agency_list):
        routes = {}
        tag_attributes = {'route' : ['tag']}
        for agency in agency_list:
            routes_list_xml = self.nextbus_requester.get_route_list_from_agency(agency)
            agency_routes = self.get_attribute_values_from_xml(
                    routes_list_xml, tag_attributes)
            routes[agency] = agency_routes['tag']
        return routes

    def get_attribute_values_from_xml(self, xml, tag_attributes):
        xml_extractor = XMLAttributesValuesExtractor(xml, tag_attributes)
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

    def initialize_extracted_data_keys_as_target_attributes(self):
        for attribute in self.target_attributes:
            self.extracted_data[attribute] = []

    def extract_values(self):
        for element in self.xml_tree:
            if element.tag == self.target_tag:
                self.extract_attribute_values_from_element(element)
        return self.extracted_data

    def extract_attribute_values_from_element(self, element):
        element_attributes = element.attrib.keys()
        for attribute in self.target_attributes:
            if attribute in element_attributes:
                self.extracted_data[attribute].append(element.attrib[attribute])


