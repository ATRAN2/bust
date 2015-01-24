import unittest
from bust import nextbus_grabber

class NextbusGrabberTest(unittest.TestCase):
    def test_tester(self):
        self.assertEqual(
                nextbus_grabber.laser(),
                'taser'
                )

