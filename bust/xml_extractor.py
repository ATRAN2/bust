from lxml import etree

class XMLAttributesValuesExtractor(object):
    def __init__(self, xml, tag_attributes_dict):
        self.extracted_data = {}
        self.xml = xml
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
