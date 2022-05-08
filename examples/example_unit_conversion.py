#unit management example
import sys
import pathlib
path = pathlib.Path(__file__).parent.parent
sys.path.append(str(path))
from measure_units import *
#temperature
t = TempUnit(25, "c")
print(f"Temp =  {t.c}C;   {t.k}K;  {t.f}F")
t.c = 100
print(f"Temp =  {t.c}C;   {t.k}K;  {t.f}F")
t.f = 212
print(f"Temp =  {t.c}C;   {t.k}K;  {t.f}F")
#concentratins
ca = Ion("ca", 30, "ppm")
print(f"Ca = {ca.mmol} mmol/l, {ca.meq} meq/l; {ca.ppm} ppm Ca, {ca.caco3} ppm CaCO3")
#latest unit was CaCO3, so add 50 ppm CaCO3
ca = ca + 50
print(f"Ca = {ca.mmol} mmol/l, {ca.meq} meq/l; {ca.ppm} ppm Ca, {ca.caco3} ppm CaCO3")
#how to deal with Pressure
p = PressureUnit(1, "atm")
print(f"1 ATM = {p.kpa} kpa")
#we can use a library to convert complex units (f.e. density)
m = WeightUnit(1.23, "g")
v = VolumeUnit(1, "cm3")
print(f"Density {m.lb/v.gal:.2f} lb/gal {m.g/v.cm3:.2f} g/cm3")
m.lb = 1
v.gal = 1
print(f"Density {m.lb/v.gal:.2f} lb/gal {m.g/v.cm3:.2f} g/cm3")
#Special unit flowrate (volume rate).
vr = VolumeRateUnit(10, "m3/hour")
print(f"Flow rate {vr.mph} m3/h {vr.gpd:.2f} gal/day")
vr.gpd = vr.gpd/10
print(f"Flow rate {vr.mph:.2f} m3/h {vr.gpd:.2f} gal/day")