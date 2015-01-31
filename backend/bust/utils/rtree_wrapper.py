from __future__ import division
from rtree import index
from collections import namedtuple
Point = namedtuple('Point', 'x y')
BoundingBox = namedtuple('BoundingBox', 'x_min y_min x_max y_max')

class RTree(object):
    def __init__(self):
        self.index = index.Index()
        self._index_id = 0

    def add_object_at_coord(self, object, coord):
        point = Point(coord[0], coord[1])
        point_as_bounding_box = BoundingBox(point.x, point.y, point.x, point.y)
        self.index.insert(self._index_id, point_as_bounding_box, object)
        self._index_id += 1

    def search_n_radius_square_around_coord(self, n_radius, coord):
        point = Point(coord[0], coord[1])
        bounding_box = BoundingBox(
            point.x - n_radius,
            point.y - n_radius,
            point.x + n_radius,
            point.y + n_radius,
        )
        results = self.search_in_bounding_box(bounding_box)
        return results

    def search_in_range(self, range):
        bounding_box = BoundingBox(range[0], range[1], range[2], range[3])
        results = self.search_in_bounding_box(bounding_box)
        return results

    def search_in_bounding_box(self, bounding_box):
        result_generator = self.index.intersection(bounding_box, True)
        return [n.object for n in result_generator]
