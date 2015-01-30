import requests
import os
import time
from .bus_datastore import BusDatastore
from bust import rtree_wrapper as rtree
from bust import pickle_wrapper as pickler
from bust import xml_extractor as xml_values_extractor

class NextbusDatastoreFactory(object):
    @staticmethod
    def generate_datastore():
        new_datastore = NextbusDatastore()
        new_datastore.populate_datastore()
        return new_datastore

class NextbusDatastore(BusDatastore):
    def __init__(self):
        BusDatastore.__init__(self)
        self.set_filename('nextbus.data')

    def find_stops_near_lat_lon(self, lat, lon):
        degrees_in_50_miles = 0.728
        search_distance = degrees_in_50_miles / 50 / 16
        stops_found = []
        while (not stops_found and search_distance <= degrees_in_50_miles):
            stops_found = self.location_rtree.search_n_radius_square_around_coords(
                    search_distance, (lat, lon))
            search_distance *= 2
        if not stops_found:
            stops_found = self.location_rtree.search_n_radius_square_around_coords(
                degrees_in_50_miles, (lat, lon))
        return stops_found

    def populate_datastore(self):
        if self.saved_data_exists():
            self.load_data_from_disk()
            populator = NextbusDatastorePopulator()
            self.location_rtree = \
                populator.populate_location_rtree_from_saved_stops(self.stops)
        else:
            populator = NextbusDatastorePopulator()
            self.stops = populator.populate_stops()
            self.save_data_to_disk()
            self.location_rtree = populator.populate_location_rtree()

    def saved_data_exists(self):
        return os.path.isfile(self.file_path)

    def save_data_to_disk(self):
        save_pickle = pickler.Pickle()
        save_pickle.dump_objects_list(self.file_path,
                [self.stops])

    def load_data_from_disk(self):
        load_pickle = pickler.Pickle()
        self.stops = load_pickle.load_to_list(self.file_path)
        self.stops = self.stops[0]

class NextbusDatastorePopulator(object):
    def __init__(self):
        self.nextbus_requester = NextbusRequester()
        self.agencies = {}
        self.routes = {}
        self.stops = {}
        self.locations = []

    def populate_stops(self):
        self.get_nextbus_data()
        return self.stops

    def populate_location_rtree_from_saved_stops(self, stops):
        self.stops = stops
        return self.populate_location_rtree()

    def populate_location_rtree(self):
        self.get_nextbus_data()
        location_rtree = self.parse_stops_data_into_location_rtree()
        return location_rtree

    def parse_stops_data_into_location_rtree(self):
        row_data = []
        location_rtree = rtree.RTree()
        self.walk_stops_dict_entries_into_locations(self.stops, row_data)
        for row in self.locations:
            lat_lon_coord, data_dict = self.format_location_row_data(row)
            location_rtree.add_object_at_coords(data_dict, lat_lon_coord)
        return location_rtree

    def walk_stops_dict_entries_into_locations(self, walk_dict, row_data):
        if 'agency_title' in walk_dict:
            agency_title = [['agency_title', walk_dict['agency_title']]]
            self.walk_stops_dict_entries_into_locations(walk_dict['route'], row_data + agency_title)
            return
        nested_dict_location = None
        for key, value in walk_dict.iteritems():
            if isinstance(value, str):
                row_data.append([key, value])
            elif isinstance(value, dict):
                nested_dict_location = value
                self.walk_stops_dict_entries_into_locations(nested_dict_location, row_data + [key])
        if not nested_dict_location:
            self.locations.append(list(row_data))

    def format_location_row_data(self, row):
        data_dict = {}
        tagless_attributes = ['agency_tag', 'route_tag', 'stop_tag']
        attribute_index = 0
        for attribute in row:
            if type(attribute) is list:
                attribute_tag = attribute[0]
                attribute_value = attribute[1]
                data_dict[attribute_tag] = attribute_value
            else:
                data_dict[tagless_attributes[attribute_index]] = attribute
                attribute_index += 1
        self.rename_street_and_stop_id_tags(data_dict)
        lat_lon_coord = (float(data_dict['lat']), float(data_dict['lon']))
        formatted_row = [lat_lon_coord, data_dict]
        return formatted_row

    def rename_street_and_stop_id_tags(self, data_dict):
        data_dict['street_title'] = data_dict.pop('title')
        if 'stopId' in data_dict:
            data_dict['stop_id'] = data_dict.pop('stopId')

    def get_nextbus_data(self):
        if not self.stops:
            self.get_agencies()
            self.get_routes()
            self.get_stops()

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
                direction_data = xml_values_extractor.NextbusXMLExtractor \
                        .get_stop_direction_data(route_stops_xml)
                self.add_direction_data_for_agency_route(direction_data, agency, route)

    def prepare_stops_dict(self):
        agency_tags = self.agencies.keys()
        for agency in agency_tags:
            self.stops[agency] = {
                    'agency_title' : self.agencies[agency],
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

    def add_direction_data_for_agency_route(self, direction_data, agency, route):
        for stop, direction_tags in direction_data.iteritems():
            entry_location = self.stops[agency]['route'][route][stop]
            for direction_tag, value in direction_tags.iteritems():
                entry_location.update({direction_tag : value})

    def wrap_row_stop_data_in_dict(self, attribute_values_lists, row_index):
        row_stop_data = []
        for attribute_values_list in attribute_values_lists:
            attribute = attribute_values_list[0]
            value = attribute_values_list[1][row_index]
            row_stop_data.append([attribute, value])
        self.append_direction_data_placeholder(row_stop_data)
        return dict(row_stop_data)

    def append_direction_data_placeholder(self, row_stop_data):
        row_stop_data.append(['direction_name', None])
        row_stop_data.append(['direction', None])


    def get_attribute_values_from_xml(self, xml, tag_attributes, parsing_root=[], attributes_filter={} ):
        xml_extractor = xml_values_extractor.XMLAttributesValuesExtractor(xml, tag_attributes)
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
        response_content = response.content
        if 'Error shouldRetry' in response_content[0:250]:
            time.sleep(25)
            response_content = self.get_response_xml_from_api_command(api_command)
        return response_content
