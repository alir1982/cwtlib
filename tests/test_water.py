import unittest
import sys
import pathlib
path = pathlib.Path(__file__).parent.parent
sys.path.append(str(path))
from water import *
from measure_units import *

class TestWater(unittest.TestCase):
    def setUp(self):
        self.water = Water(7.5, Ion("cl", 20, "ppm"), Ion("so4", 40, "ppm"), Ion("alk", 34, "caco3"), Ion("ca", 150, "caco3"), TempUnit(25, "c"), TDSUnit(320, "ppm"))
    def test_cl_set(self):
        self.assertEqual(20, self.water.cl.ppm)


    def test_lsi_simple(self):
        self.assertAlmostEqual(-0.7, self.water.lsi_simple(), 1, msg="25C")
        self.water.temp.c = 82
        self.assertAlmostEqual(0.3, self.water.lsi_simple(), 1, msg="82C")

    def test_lsi(self):
        self.water.temp.c = 25
        self.water.ca.caco3 = 500
        self.water.alk.caco3 = 340
        self.assertAlmostEqual(1.1, self.water.lsi(), 1, msg="25C")

    def test_set_cycles_correct(self):
        self.water.set_cycles(2)
        self.assertEqual(self.water.cl.ppm, 40)
        self.assertEqual(self.water.cycles, 2)
        self.assertAlmostEqual(self.water.ph, 7.3, 1)



if __name__ == "__main__":
  unittest.main()