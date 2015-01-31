import requests
import os
import time
from bust.utils import rtree_wrapper as rtree
from bust.utils import xml_extractor as xml_values_extractor

class NextBusDatastorePopulator(object):
    def __init__(self, datastore, saved_stops={}, saved_flat_index=[]):
        self._datastore = datastore
        self._agencies = {}
        self._routes = {}
        self._stops = saved_stops
        self._locations = []
        self._flat_index = saved_flat_index
        self._location_index = None

    def populate_datastore(self):
        if self._stops and self._flat_index:
            self._create_location_index_from_flat_index()
            self._datastore.location_index = self._location_index
        else:
            self._get_nextbus_data()
            self._datastore.stops = self._stops
            self._datastore.flat_index = self._flat_index
            self._datastore.location_index = self._location_index

    def _get_nextbus_data(self):
        self._get_agencies()
        self._get_routes()
        self._get_stops()
        self._parse_stops_data_into_flat_index()
        self._create_location_index_from_flat_index()

    def _get_agencies(self):
        nextbus_client = NextBusClient()
        self._agencies = nextbus_client.get_agencies()

    def _get_routes(self):
        nextbus_client = NextBusClient()
        self._routes = nextbus_client.get_routes_for_agencies(self._agencies)

    def _get_stops(self):
        nextbus_client = NextBusClient()
        self._stops = nextbus_client.get_stops_for_agencies_routes(self._agencies, self._routes)

    def _parse_stops_data_into_flat_index(self):
        self._collect_stops_entries_into_locations()
        for location in self._locations:
            lat_lon_coord, location_data = self._format_location_entry(location)
            self._flat_index.append([lat_lon_coord, location_data])

    def _create_location_index_from_flat_index(self):
        self._location_index = rtree.RTree()
        for entry in self._flat_index:
            location_coord = entry[0]
            location_data = entry[1]
            self._location_index.add_object_at_coord(location_data, location_coord)

    def _collect_stops_entries_into_locations(self):
        self._traverse_stops_data(self._stops, [])

    def _traverse_stops_data(self, traverse_map, entry_data):
        if 'agency_title' in traverse_map:
            agency_title = [['agency_title', traverse_map['agency_title']]]
            self._traverse_stops_data(traverse_map['route'], entry_data + agency_title)
            return
        nested_map_location = None
        for key, value in traverse_map.iteritems():
            if isinstance(value, str):
                entry_data.append([key, value])
            elif isinstance(value, dict):
                nested_map_location = value
                self._traverse_stops_data(nested_map_location, entry_data + [key])
        if not nested_map_location:
            self._locations.append(list(entry_data))

    def _format_location_entry(self, location):
        location_data = {}
        tagless_attributes = ['agency_tag', 'route_tag', 'stop_tag']
        attribute_index = 0
        for attribute in location:
            if type(attribute) is list:
                attribute_tag = attribute[0]
                attribute_value = attribute[1]
                location_data[attribute_tag] = attribute_value
            else:
                location_data[tagless_attributes[attribute_index]] = attribute
                attribute_index += 1
        self._rename_street_and_stop_id_tags(location_data)
        lat_lon_coord = (float(location_data['lat']), float(location_data['lon']))
        formatted_location_entry = [lat_lon_coord, location_data]
        return formatted_location_entry

    def _rename_street_and_stop_id_tags(self, location_data):
        location_data['street_title'] = location_data.pop('title')
        if 'stopId' in location_data:
            location_data['stop_id'] = location_data.pop('stopId')

class NextBusClient(object):
    NEXTBUS_API_ROOT = 'http://webservices.nextbus.com/service/publicXMLFeed'

    def __init__(self):
        self.result = {}

    def get_agencies(self):
        agencies_xml = self._query_agencies()
        tag_attributes = {'agency' : ['tag', 'title']}
        california_filter = {'regionTitle' : 'California'}
        extracted_agencies = self._get_attribute_values_from_xml(
                agencies_xml, tag_attributes, attributes_filter=california_filter)
        agency_tags = extracted_agencies['tag']
        agency_titles = extracted_agencies['title']
        self.result = dict(zip(agency_tags, agency_titles))
        return self.result

    def get_routes_for_agencies(self, agencies):
        agency_tags = agencies.keys()
        tag_attributes = {'route' : ['tag']}
        for agency in agency_tags:
            agency_routes_xml = self._query_route_list_from_agency(agency)
            agency_routes = self._get_attribute_values_from_xml(
                    agency_routes_xml, tag_attributes)
            self.result[agency] = agency_routes['tag']
        return self.result

    def get_stops_for_agencies_routes(self, agencies, routes):
        self._prepare_stops_dict(agencies)
        tag_attributes = {'stop' : ['tag', 'title', 'lat', 'lon', 'stopId']}
        xml_parsing_root = [0]
        agencies = routes.keys()
        for agency in agencies:
            agency_routes = routes[agency]
            for route in agency_routes:
                route_stops_xml = self._query_route_stops(agency, route)
                route_stops = self._get_attribute_values_from_xml(
                        route_stops_xml, tag_attributes, xml_parsing_root)
                self._add_stop_data_for_agency_route(route_stops, agency, route)
                direction_data = xml_values_extractor.NextBusXMLExtractor \
                        .get_stop_direction_data(route_stops_xml)
                self._add_direction_data_for_agency_route(direction_data, agency, route)
        return self.result

    def _query_agencies(self):
        api_params = {'command' : 'agencyList'}
        return self._get_response_xml_from_api_params(api_params)

    def _query_route_list_from_agency(self, agency):
        api_params = {'command' : 'routeList', 'a' : agency}
        return self._get_response_xml_from_api_params(api_params)

    def _query_route_stops(self, agency, route_tag):
        api_params = {'command': 'routeConfig', 'a' : agency, 'r' : route_tag}
        return self._get_response_xml_from_api_params(api_params)

    def _get_response_xml_from_api_params(self, api_params):
        while True:
            response = requests.get(self.NEXTBUS_API_ROOT, params=api_params)
            if 'Error shouldRetry' in response.content[0:250]:
                # NextBus has a data limit of 4MB / 20 seconds
                time.sleep(25)
                continue
            else:
                return response.content

    def _make_api_url_from_api_endpoint_params(self, api_endpoint, api_params):
        api_url = self.NEXTBUS_API_ROOT + api_endpoint + '&'
        for param, value in api_params.iteritems():
            api_url += param + '=' + value + '&'
        api_url = api_url[:-1]
        return api_url

    def _prepare_stops_dict(self, agencies):
        agency_tags = agencies.keys()
        for agency in agency_tags:
            self.result[agency] = {
                'agency_title' : agencies[agency],
                'route' : {},
            }

    def _add_stop_data_for_agency_route(self, route_stops, agency, route):
        attribute_values_collection = []
        self.result[agency]['route'][route] = {}
        new_entry_location = self.result[agency]['route'][route]
        for attribute, values in route_stops.iteritems():
            if attribute is 'tag':
                stop_tags = values
            else:
                attribute_values_collection.append([attribute, values])
        for entry_index in range(len(stop_tags)):
            stop_data_entry = self._format_stop_data_entry(
                attribute_values_collection, entry_index)
            new_entry_location.update({stop_tags[entry_index] : stop_data_entry})

    def _format_stop_data_entry(self, attribute_values_collection, entry_index):
        stop_data_entry = []
        for attribute_values in attribute_values_collection:
            attribute = attribute_values[0]
            value = attribute_values[1][entry_index]
            stop_data_entry.append([attribute, value])
        self._append_direction_data_placeholder(stop_data_entry)
        return dict(stop_data_entry)

    def _append_direction_data_placeholder(self, stop_data_entry):
        stop_data_entry.append(['direction_name', None])
        stop_data_entry.append(['direction', None])

    def _add_direction_data_for_agency_route(self, direction_data, agency, route):
        for stop, direction_tags in direction_data.iteritems():
            entry_location = self.result[agency]['route'][route][stop]
            for direction_tag, value in direction_tags.iteritems():
                entry_location.update({direction_tag : value})

    def _get_attribute_values_from_xml(self, xml, tag_attributes, parsing_root=[], attributes_filter={} ):
        xml_extractor = xml_values_extractor.XMLAttributesValuesExtractor(xml, tag_attributes)
        xml_extractor.set_attributes_filter(attributes_filter)
        xml_extractor.set_parsing_root(parsing_root)
        extracted_data = xml_extractor.extract_values()
        return extracted_data


