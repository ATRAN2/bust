from bust import bus_datastore
from bust.components import nextbus_grabber

def create_datastore_from_nextbus_to_file():
    new_datastore = bus_datastore.NextBusDatastore()
    datastore_populator = nextbus_grabber.NextBusDatastorePopulator(new_datastore)
    datastore_populator.populate_from_nextbus()
    new_datastore.save_data()

if __name__ == '__main__':
	create_datastore_from_nextbus_to_file()
