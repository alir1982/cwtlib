import unittest
import sys
import pathlib
path = pathlib.Path(__file__).parent.parent
sys.path.append(str(path))
from water import *
from measure_units import *
from tower import *

class TestTower(unittest.TestCase):
    def setUp(self):
        self.tower = Tower(Air(TempUnit(20, "c"), HumidityUnit(50, "proc"), PressureUnit(1013, "hpa")), TempUnit(25, "c"), TempUnit(20, "c"), VolumeUnit(1000, "m3"),
                           VolumeRateUnit(1000, "m3/hour"))

    def test_evaporation_thermo(self):
        self.assertAlmostEqual(self.tower.evaporation_thermo().value, 15.8, 0)

    def test_evaporation_snip(self):
        self.assertAlmostEqual(self.tower.evaporation("snip").value, 15.2, 0)

    def test_evaporation_kurita(self):
        self.assertAlmostEqual(self.tower.evaporation("kurita").value, 15.4, 0)

    def test_efficacy(self):
        self.assertAlmostEqual(self.tower.efficacy(), 0.41, 1)

    def test_lg_ratio(self):
        self.assertAlmostEqual(self.tower.lg_ratio(), 2.33, 1)

    def test_set_cycles(self):
        self.tower.set_cycles(2)
        self.assertAlmostEqual(self.tower.evaporation().value*2, self.tower.mu.value, 1)
        self.assertAlmostEqual(self.tower.hti.value, 30, 0)

unittest.main()