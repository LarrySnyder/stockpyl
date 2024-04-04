import unittest
from stockpyl.temp import sq
from tests.settings import *

class TestSq(unittest.TestCase):
	def test_sq(self):
		self.assertEqual(sq(2), 4)
