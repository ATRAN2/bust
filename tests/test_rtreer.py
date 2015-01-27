import unittest
from bust import rtreer

class RTreeTest(unittest.TestCase):
    def test_add_object_at_coords(self):
        test_rtree = rtreer.RTree()
        test_object = {'test' : 'object'}
        test_rtree.add_object_at_coords(test_object, (0.5, 0.5))
        self.assertTrue(
            test_object in test_rtree.search_in_range((0.25, 0.25, 0.75, 0.75)))

    def test_search_n_size_square_around_point(self):
        test_rtree = rtreer.RTree()
        test_objects_coords = [
            [{'test1' : 'object1'}, (1, 1)],
            [{'test2' : 'object2'}, (-1, -1)],
            [{'test3' : 'object3'}, (9, 6)],
            ]
        for test_item in test_objects_coords:
            test_rtree.add_object_at_coords(test_item[0], test_item[1])
        square_search = test_rtree.search_n_radius_square_around_coords(5, (5, 5))
        self.assertTrue(test_objects_coords[0][0] in square_search)
        self.assertFalse(test_objects_coords[1][0] in square_search)
        self.assertTrue(test_objects_coords[2][0] in square_search)

if __name__ == '__main__':
    unittest.main()
