import cPickle as pickle

class Serializer(object):
    @classmethod
    def serialize(cls, dump_objects):
        return pickle.dumps(dump_objects, pickle.HIGHEST_PROTOCOL)

    @classmethod
    def deserialize(cls, serialized_data):
        return pickle.loads(serialized_data)
