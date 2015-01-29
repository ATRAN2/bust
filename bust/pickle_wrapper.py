import cPickle as pickle

class Pickle(object):
    def dump_objects_list(self, filepath, objects_list):
        with open(filepath, 'wb') as out:
            for object in objects_list:
                pickle.dump(object, out, pickle.HIGHEST_PROTOCOL)

    def load_to_list(self, filepath):
        objects_list = []
        objects_to_read_remaining = True
        with open(filepath, 'rb') as input:
            while objects_to_read_remaining:
                try:
                    objects_list.append(pickle.load(input))
                except EOFError as e:
                    objects_to_read_remaining = False
        return objects_list
