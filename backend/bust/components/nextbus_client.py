import time

import requests

from bust.utils import xml_extractor as xml_values_extractor
from bust import config


class NextBusClient(object):
    """
    Send Request to the NextBus API endpoints, send data to  xml_extractor
    to parse, then return formmated data.
    """

    NEXTBUS_API_ROOT = 'http://webservices.nextbus.com/service/publicXMLFeed'

    def __init__(self):
        self.stops = {}

    def get_agencies(self):
        """ Query the NextBus API and get agency tags and agency titles  """
        agencies_xml = self._query_agencies()
        tag_attributes = {'agency' : ['tag', 'title']}
        agency_filter = {'regionTitle' : config.AGENCY_REGION}
        extracted_agencies = self._get_attribute_values_from_xml(
                agencies_xml, tag_attributes, attributes_filter=agency_filter)
        agency_tags = extracted_agencies['tag']
        agency_titles = extracted_agencies['title']
        agencies = dict(zip(agency_tags, agency_titles))
        return agencies

    def get_routes_for_agencies(self, agencies):
        """ 
        For each of the agencies query the NextBus API and collect all
        the route tags for that agency.
        """

        routes = {}
        agency_tags = agencies.keys()
        tag_attributes = {'route' : ['tag']}
        for agency in agency_tags:
            agency_routes_xml = self._query_route_list_from_agency(agency)
            agency_routes = self._get_attribute_values_from_xml(
                    agency_routes_xml, tag_attributes)
            routes[agency] = agency_routes['tag']
        return routes

    def get_stops_for_agencies_routes(self, agencies, routes):
        """ Return stop data for each route of each agency """
        self.stops = {}
        self._prepare_stops_map(agencies)
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
                direction_data = xml_values_extractor.NextBusDirectionsExtractor\
                        .get_stop_direction_data(route_stops_xml)
                self._add_direction_data_for_agency_route(direction_data, agency, route)
        return self.stops

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

    def _prepare_stops_map(self, agencies):
        agency_tags = agencies.keys()
        for agency in agency_tags:
            self.stops[agency] = {
                'agency_title' : agencies[agency],
                'route' : {},
            }

    def _add_stop_data_for_agency_route(self, route_stops, agency, route):
        attribute_values_collection = []
        self.stops[agency]['route'][route] = {}
        new_entry_location = self.stops[agency]['route'][route]
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
            entry_location = self.stops[agency]['route'][route][stop]
            for direction_tag, value in direction_tags.iteritems():
                entry_location.update({direction_tag : value})

    def _get_attribute_values_from_xml(self, xml, tag_attributes, parsing_root=None, attributes_filter=None):
        parsing_root = parsing_root or []
        attributes_filter = attributes_filter or {}
        xml_extractor = xml_values_extractor.XMLAttributesValuesExtractor(xml, tag_attributes)
        xml_extractor.set_attributes_filter(attributes_filter)
        xml_extractor.set_parsing_root(parsing_root)
        extracted_data = xml_extractor.extract_values()
        return extracted_data

