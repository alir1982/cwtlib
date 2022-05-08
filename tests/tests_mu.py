import unittest
import sys
import pathlib
path = pathlib.Path(__file__).parent.parent
sys.path.append(str(path))
#Конвертация температуры
from measure_units import *



class TestMeasureUnit(unittest.TestCase):
    def setUp(self):
        pass

    def test_basic(self):
        self.basic_param = MeasureUnit(20, u="complex")
        self.basic_param.unit = "simple"
        self.assertEqual(self.basic_param.value, 5, "Неправильная конвертация во внутреннюю ЕИ")
        self.basic_param.value = 10
        self.basic_param.unit = "complex"
        self.assertEqual(self.basic_param.value, 30, "Неправильная конвертация во внешнюю ЕИ")
        self.assertEqual(self.basic_param.i_value, 10, "Повреждение внутренней единицы")
    
    def test_tempp(self):
        self.temp = TempUnit(0, "c")
        self.temp.unit = "k"
        self.assertAlmostEqual(self.temp.value, 273, 0, "0С примерно равен 273")
        self.assertEqual(self.temp.value, 273.15, "0С равен 273.15")
        self.temp.unit = "f"
        self.assertEqual(self.temp.value, 32, "0С равен 32Ф")
        self.temp.value = 212
        self.temp.unit = "c"
        self.assertEqual(self.temp.value, 100, "212Ф равен 100С")
        with self.assertRaises(Exception):
            self.temp.unit = "DF" 
        self.assertEqual(self.temp.unit, "c", "куда то слетела размерность")
    
    def test_ariphmetic(self):
        temp = TempUnit(0, "c")
        temp.unit = "k"
        temp = temp + 100
        self.assertAlmostEqual(temp.value, 373, 0, "0С + 100К = 373К")
    
    def test_conc(self):
        cl = Ion("cl", 71, "ppm")
        cl.unit = "meq"
        self.assertEqual(cl.value, 2, "2 мг-экв/л хлорида это 71 ppm")
        alk = Ion("hco3", 2, "meq")
        alk.unit = "caco3"
        self.assertEqual(alk.value, 100, "2 мг-экв щелочности это 100 мг/л как карбоната кальция")
    
    def test_magic(self):
        cl = Ion("cl", 71, "ppm")
        self.assertEqual(cl.ppm, 71, "Магия геттера")
        cl.meq = 1.5
        self.assertEqual(cl.caco3, 75, "Магия сеттера и геттера")
    
    def test_power(self):
        p = PowerUnit(1000, "kw")
        self.assertEqual(p.mw, 1.0)
        self.assertAlmostEqual(p.kcalh,  859845.228, 0)
        self.assertAlmostEqual(p.btuh, 3414424.784)
        self.assertEqual(1000000, p.w)

    def test_heat(self):
        h = HeatUnit(1000, "kj")
        self.assertAlmostEqual(h.kcal, 238.845889, 0)
        self.assertEqual(h.j, 1000000)

    def test_ariphmetic_ion(self):
        mg = Ion("mg", 2, "meq")
        ca = Ion("ca", 100, "caco3")
        hrd = ca + mg
        self.assertEqual(hrd.caco3, 200)
        ca = hrd - mg
        self.assertEqual(ca.caco3, 100)
    def test_pressure(self):
        p = PressureUnit(1, "atm")
        self.assertEqual(101.325, p.kpa)
        self.assertEqual(101325, p.pa)
        self.assertEqual(760, p.hg)
        self.assertEqual(1013.25, p.hpa)

    def test_length(self):
        l = LengthUnit(1, "inches")
        self.assertAlmostEqual(2.54, l.cm, 2)
        self.assertAlmostEqual(0.0254, l.m, 4)
        self.assertAlmostEqual(25.4, l.mm, 1)
    def test_volume(self):
        v = VolumeUnit(1, "pinta")
        self.assertAlmostEqual(0.473, v.l, 3)
        self.assertAlmostEqual(473, v.cm3, 0)
        self.assertAlmostEqual(1/8, v.gal, 5)
        v.barrel = 1
        self.assertAlmostEqual(31.5, v.gal, 1)
        self.assertAlmostEqual(31.5*8, v.pinta, 1)
    def test_weight(self):
        m = WeightUnit(1, "lb")
        self.assertAlmostEqual(16, m.ounce, 1)
        self.assertAlmostEqual(453.6, m.g, 1)
        self.assertAlmostEqual(0.4536, m.kg, 4)
    def test_humidity(self):
        h = HumidityUnit(50, "proc")
        self.assertAlmostEqual(0.5, h.ratio, 2)
    def test_tds(self):
        tds = TDSUnit(1000, "ppm")
        self.assertAlmostEqual(2000, tds.usm, 0)

    def test_mols(self):
        ca = Ion("ca", 6, "meq")
        self.assertEqual(3, ca.mmol)
        self.assertEqual(0.003, ca.mol)
        self.assertEqual(300, ca.caco3)

    def test_times(self):
        t = TimeUnit(1, "day")
        self.assertEqual(24, t.hour)
        self.assertEqual(1/365, t.year)

    def test_volume_rate(self):
        vr = VolumeRateUnit(1, "m3/hour")
        vr.unit = "gal/day"
        self.assertAlmostEqual(6.342, vr.value/1000, 1)
        vr.value = 10000
        print(vr.volume.unit, vr.time.unit)
        print(vr.volume.value, vr.time.value)
        vr.unit = "m3/hour"
        self.assertAlmostEqual(1.58, vr.value, 1)

    



# Executing the tests in the above test case class
if __name__ == "__main__":
  unittest.main()