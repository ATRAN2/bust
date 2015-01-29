from __future__ import division
from rtree import index

class RTree(object):
    def __init__(self):
        self.idx = index.Index()
        self.pk = 0

    def add_object_at_coords(self, object, coords):
        point = Point(coords[0], coords[1])
        self.add_object_at_point(object, point)

    def add_object_at_point(self, object, point):
        self.idx.insert(self.pk, point.as_bounding_box_tuple(), object)
        self.pk += 1

    def search_n_radius_square_around_coords(self, n_radius, coords):
        point = Point(coords[0], coords[1])
        results = self.search_n_radius_square_around_point(n_radius, point)
        return results

    def search_n_radius_square_around_point(self, n_radius, point):
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
        result_generator = self.idx.intersection(bounding_box.as_tuple(), True)
        return [n.object for n in result_generator]

class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def as_bounding_box_tuple(self):
        return (self.x, self.y, self.x, self.y)

class BoundingBox(object):
    def __init__(self, min_x, min_y, max_x, max_y):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y

    def as_tuple(self):
        return (self.min_x, self.min_y, self.max_x, self.max_y)
