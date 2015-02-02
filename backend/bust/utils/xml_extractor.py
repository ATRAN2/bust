from lxml import etree

class XMLAttributesValuesExtractor(object):
    def __init__(self, xml, tag_attributes_map):
        self.extracted_data = {}
        self.parsing_root = []
        self.attributes_filter = {}
        self._xml_tree = etree.XML(xml)
        self._target_tag = tag_attributes_map.keys()[0]
        self._target_attributes = tag_attributes_map.values()[0]
        self._initialize_extracted_data_keys_as_target_attributes()

    def set_parsing_root(self, parsing_root):
        self.parsing_root = parsing_root

    def set_attributes_filter(self, attributes_filter):
        self.attributes_filter = attributes_filter

    def extract_values(self):
        self._move_to_parsing_root()
        for element in self._xml_tree:
            if element.tag == self._target_tag and \
            self._has_filter_attributes(element):
                self._extract_attribute_values_from_element(element)
        return self.extracted_data

    def _initialize_extracted_data_keys_as_target_attributes(self):
        for attribute in self._target_attributes:
            self.extracted_data[attribute] = []

    def _move_to_parsing_root(self):
        while self.parsing_root:
            self._xml_tree = self._xml_tree[self.parsing_root[0]]
            self.parsing_root = self.parsing_root[1:]

    def _extract_attribute_values_from_element(self, element):
        element_attributes = element.attrib.keys()
        for attribute in self._target_attributes:
            if attribute in element_attributes:
                self.extracted_data[attribute].append(element.attrib[attribute])
            else:
                self.extracted_data[attribute].append(None)

    def _has_filter_attributes(self, element):
        if not self.attributes_filter:
            return True
        element_has_filter_attributes = True
        for attribute, value in self.attributes_filter.iteritems():
            if (attribute not in element.attrib) or \
                (value not in element.attrib[attribute]):
                element_has_filter_attributes = False
                break
        return element_has_filter_attributes

class NextBusDirectionsExtractor(object):
    @classmethod
    def get_stop_direction_data(cls, stop_xml):
        directions_tree = etree.XML(stop_xml)
        directions = cls._find_elements_in_xml_tree_with_tag(
                directions_tree, 'direction')
        direction_data = {}
        for direction_element in directions:
            cls._put_element_data_into_direction_data(direction_element, direction_data)
        return direction_data

    @classmethod
    def _put_element_data_into_direction_data(cls, direction_element, direction_data):
        title_tag = direction_element.attrib['title']
        name_tag = direction_element.attrib['name']
        stop_tags = cls._get_direction_stop_tags(direction_element)
        for stop_tag in stop_tags:
            direction_data[stop_tag] = \
                {'direction' : title_tag, 'direction_name' : name_tag}

    @classmethod
    def _get_direction_stop_tags(cls, direction_element):
        stop_tags = []
        for stop in direction_element.iterchildren():
            stop_tags.append(stop.attrib['tag'])
        return stop_tags

    @classmethod
    def _find_elements_in_xml_tree_with_tag(cls, xml_tree, tag):
        return xml_tree.iter(tag)

