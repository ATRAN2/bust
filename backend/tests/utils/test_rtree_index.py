import unittest

from bust.utils import rtree_index as rtree


class RTreeTest(unittest.TestCase):
    def test_add_object_at_coord(self):
        test_rtree = rtree.RTree()
        test_object = {'test' : 'object'}
        test_rtree.add_object_at_coord(test_object, (0.5, 0.5))
        self.assertTrue(
            test_object in test_rtree.search_in_range((0.25, 0.25, 0.75, 0.75)))

    def test_search_n_distance_around_point(self):
        test_rtree = rtree.RTree()
        test_objects_coords = [
            [{'test1' : 'object1'}, (1, 1)],
            [{'test2' : 'object2'}, (-1, -1)],
            [{'test3' : 'object3'}, (9, 6)],
            ]
        for test_item in test_objects_coords:
            test_rtree.add_object_at_coord(test_item[0], test_item[1])
        square_search = test_rtree.search_n_distance_around_coord(5, (5, 5))
        self.assertTrue(test_objects_coords[0][0] in square_search)
        self.assertFalse(test_objects_coords[1][0] in square_search)
        self.assertTrue(test_objects_coords[2][0] in square_search)

if __name__ == '__main__':
    unittest.main()
