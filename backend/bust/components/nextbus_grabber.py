from bust.utils import rtree_index
from bust.components import nextbus_client
from bust import config


class NextBusDatastorePopulator(object):
    """
    Takes an empty NextBusDatastore instance and populate it with stops
    data from the NextBus API or from file. Take formatted data from
    NextBusClient and create NextBusDatastore's location index.
    """

    def __init__(self, datastore):
        self._datastore = datastore
        self._nextbus_client = nextbus_client.NextBusClient()
        self._agencies = {}
        self._routes = {}
        self._stops = {}
        self._locations = []
        self._location_index = None

    def populate_from_nextbus(self):
        """ Populate the datastore gathering data from the NextBus API """
        self._get_nextbus_data()
        self._datastore.stops = self._stops
        self._datastore.location_index = self._location_index

    def populate_from_file(self):
        """ Populate the datastore from serialized data """
        self._datastore.load_data()
        self._stops = self._datastore.stops
        self._parse_stops_data_into_location_index()
        self._datastore.location_index = self._location_index

    def _get_nextbus_data(self):
        self._get_agencies()
        self._get_routes()
        self._get_stops()
        self._parse_stops_data_into_location_index()

    def _get_agencies(self):
        self._agencies = self._nextbus_client.get_agencies()

    def _get_routes(self):
        self._routes = self._nextbus_client.get_routes_for_agencies(self._agencies)

    def _get_stops(self):
        self._stops = self._nextbus_client.get_stops_for_agencies_routes(self._agencies, self._routes)

    def _parse_stops_data_into_location_index(self):
        self._location_index = rtree_index.RTree()
        self._collect_stops_entries_into_locations()
        for location in self._locations:
            lat_lon_coord, location_data = self._format_location_entry(location)
            self._location_index.add_object_at_coord(location_data, lat_lon_coord)

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

