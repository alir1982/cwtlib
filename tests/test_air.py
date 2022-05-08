import unittest
import sys
import pathlib
path = pathlib.Path(__file__).parent.parent
sys.path.append(str(path))
from water import *
from measure_units import *
from tower import *

class TestAir(unittest.TestCase):
    def setUp(self):
        self.air = Air(tair=TempUnit(30, "c"), hair=HumidityUnit(50, "proc"), pair=PressureUnit(750, "hg"))
    def test_evaporation_snip(self):
        self.assertAlmostEqual(0.0015, self.air.evaporation_snip(), 2)
        self.air.tair.c = 0
        self.assertAlmostEqual(0.001, self.air.evaporation_snip(), 2)
        self.air.tair.c = 10
        self.assertAlmostEqual(0.0012, self.air.evaporation_snip(), 2)
        self.air.tair.c = 20
        self.assertAlmostEqual(0.0014, self.air.evaporation_snip(), 2)
    def test_evaporation_kurita(self):
        self.air.tair.c = 0
        self.assertAlmostEqual(0.001, self.air.evaporation_kurita(), 2)

    def test_wb(self):
        self.air.tair.c = 30
        self.air.hair.perc = 36.35
        print(self.air.dew_temp().c)
        print(self.air.wet_bulb().c)
        print(self.air.wet_bulb_temp().c)
        self.assertAlmostEqual(20, self.air.wet_bulb_temp().c, 1)
        self.assertAlmostEqual(20, self.air.wet_bulb().c, 1)
        self.assertAlmostEqual(20, self.air.dew_temp().c, 1)




# Executing the tests in the above test case class
if __name__ == "__main__":
  unittest.main()