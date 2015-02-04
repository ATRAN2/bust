import cPickle as pickle


class Serializer(object):
    """ Serialize data for saving and loading """

    @classmethod
    def serialize(cls, dump_objects):
        """ Serialie data for saving """
        return pickle.dumps(dump_objects, pickle.HIGHEST_PROTOCOL)

    @classmethod
    def deserialize(cls, serialized_data):
        """ Deserialize data for loading """
        return pickle.loads(serialized_data)
