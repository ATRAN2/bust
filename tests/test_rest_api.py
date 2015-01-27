import unittest
from bust import main

@unittest.skip('REST API TODO after Bus Datastore')
class RestAPITest(unittest.TestCase):
    def test_get_page(self):
        app = main.app.test_client()
        response = app.get('/api')
        self.assertIn('This is the api home.', response.data)

if __name__ == '__main__':
    unittest.main()
