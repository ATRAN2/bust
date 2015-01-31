import os
import unittest
from bust.utils.pickle_wrapper import Serializer

class SerializerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.objects = [
            ['test_list1', 'test_list2'],
            {'test_dict_key' : 'test_dict_value'},
            13.4,
        ]

    def test_serialize_deserialize(self):
        serialized_objects = Serializer.serialize(self.objects)
        self.assertNotEqual(serialized_objects, self.objects)

        deserialized_objects = Serializer.deserialize(serialized_objects)
        self.assertEqual(self.objects, deserialized_objects)

if __name__ == '__main__':
    unittest.main()
