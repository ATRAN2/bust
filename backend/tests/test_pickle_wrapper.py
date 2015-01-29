import os
import unittest
from bust import pickle_wrapper

class PickleWrapperTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pickler = pickle_wrapper.Pickle()
        cls.filename = 'pickle_test.pkl'
        cls.objects = [
            ['test_list1', 'test_list2'],
            {'test_dict_key' : 'test_dict_value'},
            13.4,
        ]

    def test_dump_objects_list(self):
        self.pickler.dump_objects_list(self.filename, self.objects)
        self.assertTrue(os.path.isfile(self.filename))
        os.remove(self.filename)

    def test_load_to_list(self):
        self.pickler.dump_objects_list(self.filename, self.objects)
        loaded_objects = self.pickler.load_to_list(self.filename)
        self.assertEqual(self.objects, loaded_objects)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.filename)

if __name__ == '__main__':
    unittest.main()
