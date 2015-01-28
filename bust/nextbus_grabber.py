import requests
from lxml import etree
from .bus_datastore import BusDatastore
from bust import rtree_wrapper as rtree

class NextbusDatastoreFactory(object):
    @staticmethod
    def generate_datastore():
        new_datastore = NextbusDatastore()
        new_datastore.populate_datastore()
        return new_datastore

class NextbusDatastore(BusDatastore):
    def __init__(self):
        BusDatastore.__init__(self)

    def find_stops_near_lat_lon(self, lat, lon):
        pass

    def populate_datastore(self):
        populator = NextbusDatastorePopulator()

class NextbusDatastorePopulator(object):
    def __init__(self):
        self.nextbus_requester = NextbusRequester()
        self.agencies = {}
        self.routes = {}
        self.stops = {}
        self.locations = {}

    def populate_location_rtree(self, agencies, routes):
        if not self.stops_data():
            get_stops_data(routes)

    def get_bus_data(self):
        if not self.stop_data:
            get_agencies()
            get_routes()
            get_stops()

    def get_agencies(self):
        agencies_xml = self.nextbus_requester.get_agencies()
        tag_attributes = {'agency' : ['tag', 'title']}
        california_filter = {'regionTitle' : 'California'}
        extracted_agencies = self.get_attribute_values_from_xml(
                agencies_xml, tag_attributes, attributes_filter=california_filter)
        agency_tags = extracted_agencies['tag']
        agency_titles = extracted_agencies['title']
        self.agencies = dict(zip(agency_tags, agency_titles))

    def get_routes(self):
        agency_tags = self.agencies.keys()
        tag_attributes = {'route' : ['tag']}
        for agency in agency_tags:
            agency_routes_xml = self.nextbus_requester.get_route_list_from_agency(agency)
            agency_routes = self.get_attribute_values_from_xml(
                    agency_routes_xml, tag_attributes)
            self.routes[agency] = agency_routes['tag']

    def get_stops(self):
        self.prepare_stops_dict()
        tag_attributes = {'stop' : ['tag', 'title', 'lat', 'lon', 'stopId']}
        xml_parsing_root = [0]
        agencies = self.routes.keys()
        for agency in agencies:
            agency_routes = self.routes[agency]
            for route in agency_routes:
                route_stops_xml = self.nextbus_requester.get_route_stops(agency, route)
                route_stops = self.get_attribute_values_from_xml(
                        route_stops_xml, tag_attributes, xml_parsing_root)
                self.add_stop_data_for_agency_route(route_stops, agency, route)

    def prepare_stops_dict(self):
        agency_tags = self.agencies.keys()
        for agency in agency_tags:
            self.stops[agency] = {
                    'title' : self.agencies[agency],
                    'route' : {},
            }

    def add_stop_data_for_agency_route(self, route_stops, agency, route):
        attribute_values_list = []
        self.stops[agency]['route'][route] = {}
        new_entry_location = self.stops[agency]['route'][route]
        for attribute, values in route_stops.iteritems():
            if attribute is 'tag':
                stop_tags = values
            else:
                attribute_values_list.append([attribute, values])
        for row_index in range(len(stop_tags)):
            row_stop_data = self.wrap_row_stop_data_in_dict(attribute_values_list, row_index)
            new_entry_location.update({stop_tags[row_index] : row_stop_data})
            self.add_row_data_to_locations(agency, row_stop_data)

    def wrap_row_stop_data_in_dict(self, attribute_values_lists, row_index):
        row_stop_data = []
        for attribute_values_list in attribute_values_lists:
            attribute = attribute_values_list[0]
            value = attribute_values_list[1][row_index]
            row_stop_data.append([attribute, value])
        return dict(row_stop_data)

    def add_row_data_to_locations(self, agency, row_stop_data):
        lat_lon_key = (
                float(row_stop_data['lat']),
                float(row_stop_data['lon'])
        )
        data_value = {
                'agency_tag' : agency,
                'agency_title' : self.agencies[agency],
                'street_title' : row_stop_data['title'],
                'lat' : row_stop_data['lat'],
                'lon' : row_stop_data['lon'],
                'stop_id' : row_stop_data['stopId'],
        }
        self.locations[lat_lon_key] = data_value

    def get_attribute_values_from_xml(self, xml, tag_attributes, parsing_root=[], attributes_filter={} ):
        xml_extractor = XMLAttributesValuesExtractor(xml, tag_attributes)
        xml_extractor.set_attributes_filter(attributes_filter)
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

    def set_attributes_filter(self, attributes_filter):
        self.attributes_filter = attributes_filter

    def extract_values(self):
        self.move_to_parsing_root()
        for element in self.xml_tree:
            if element.tag == self.target_tag and \
            self.has_filter_attributes(element):
                self.extract_attribute_values_from_element(element)
        return self.extracted_data

    def move_to_parsing_root(self):
        while self.parsing_root:
            self.xml_tree = self.xml_tree[self.parsing_root[0]]
            self.parsing_root = self.parsing_root[1:]

    def extract_attribute_values_from_element(self, element):
        element_attributes = element.attrib.keys()
        for attribute in self.target_attributes:
            if attribute in element_attributes:
                self.extracted_data[attribute].append(element.attrib[attribute])
            else:
                self.extracted_data[attribute].append(None)

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
