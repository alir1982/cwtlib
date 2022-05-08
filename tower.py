import math
import numpy as np
from copy import deepcopy
from measure_units import *
import requests
import os
import pathlib
import sys
path = pathlib.Path(__file__).parent
sys.path.append(str(path))

try:
    TOKEN = os.environ["OpenWeatherMap"]
except:
    TOKEN = None

class Air:
    '''
    Передаем температуру, влажность и давление
    '''
    def __init__(self, tair=TempUnit(25, "c"), hair=HumidityUnit(0.5, "ratio"), pair=PressureUnit(748, "hg")):
        self.tair, self.hair, self.pair = tair, hair, pair

    '''
    либо загружаем ее из OpenWeatherMap
    '''
    def load_weather_conditions(self, loc):
        if TOKEN:
            weather = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={loc}&APPID={TOKEN}&units=metric").json()
            self.tair = TempUnit(weather["main"]["temp"], "c")
            self.hair = HumidityUnit(weather["main"]["humidity"], "proc")
            self.pair = PressureUnit(weather["main"]["pressure"], "hpa")
        else:
            raise Exception("PLEASE set openweathermap API  token as an environmental variable OpenWeatherMap")

    def evaporation_snip(self):
        self.ev_coeff = (0.0009971 + 0.00002357 * (self.tair.c) - 0.0000002143 * (self.tair.c)**2)
        return self.ev_coeff

    def evaporation_kurita(self):
        self.ev_coeff = (0.575 + 0.011 * self.tair.c) / 580
        return self.ev_coeff

    def pressure_of_saturated_vapor(self):
        return PressureUnit(math.exp((1500.3+23.5*self.tair.c)/(234 + self.tair.c)), 'pa')

    def pressure_of_vapor(self):
        return self.pressure_of_saturated_vapor()*self.hair.ratio

    def content_of_water(self):
        return 622*self.pressure_of_vapor().pa/(self.pair.pa - self.pressure_of_vapor().pa)

    def heat_of_evaporasation(self):
        ans = HeatUnit(-2.362*self.tair.c + 2501, "j")
        return ans

    def enthalpy_wet_air(self):
        ans = HeatUnit(1.006*self.tair.c + (self.heat_of_evaporasation().j + 1.86*self.tair.c)*self.content_of_water()/1000, "j")
        return ans

    def wet_bulb_temp(self):
        ent = self.enthalpy_wet_air().j
        self.wb = TempUnit((-6.14+0.651*ent)/(1+0.0097*ent - 0.00000312 * ent**2), "c")
        return self.wb

    def wet_bulb(self):
        wb = self.tair.c * np.arctan(0.151977 * (self.hair.proc + 8.313659) ** 0.5) + \
             np.arctan(self.tair.c + self.hair.proc) - np.arctan(self.hair.proc - 1.676331) + \
             0.00391838 * self.hair.proc ** 1.5 * np.arctan(0.023101 * self.hair.proc) - 4.686035
        ans = TempUnit(wb, "c")
        return ans

    def dew_temp(self):
        a = np.log(self.hair.ratio) + 17.62 * self.tair.c / (243.12 + self.tair.c)
        dt = 243.12 * a / (17.62 - a)
        return TempUnit(dt, "c")


class Tower:

    def __init__(self, rr=VolumeRateUnit(2100, "m3/hour"), vol=VolumeUnit(650, "m3"), thot=TempUnit(30, "c"), tcold=TempUnit(25, "c"), air=Air()):
        self.air = air
        self.rr = rr
        self.vol = vol
        self.thot = thot
        self.tcold = tcold

    def lg_ratio(self):
        delta_enthalpy_of_water = HeatUnit(4.18 * (self.thot.c - self.tcold.c), "j")
        enthalpy_cold_air = self.air.enthalpy_wet_air().j
        hair = deepcopy(self.air.hair)
        tair = deepcopy(self.air.tair)
        self.air.hair = HumidityUnit(100, "proc")
        self.air.tair = self.thot
        enthalpy_hot_air = self.air.enthalpy_wet_air().j
        self.air.hair = hair
        self.air.tair = tair
        return (enthalpy_hot_air - enthalpy_cold_air) / delta_enthalpy_of_water.j

    def evaporation_thermo(self):
        x = self.lg_ratio()
        was_water = self.air.content_of_water()
        hair = self.air.hair
        tair = self.air.tair
        self.air.hair = HumidityUnit(100, "proc")
        self.air.tair = self.thot
        became_water = self.air.content_of_water()
        self.air.hair = hair
        self.air.tair = tair
        self.ev = VolumeRateUnit((became_water - was_water) / x / 1000*self.rr.value, self.rr.unit)
        return self.ev

    def evaporation(self, tip="snip"):
        if tip == "snip":
            self.ev = VolumeRateUnit(self.air.evaporation_snip()*(self.thot.c - self.tcold.c)*self.rr.value, self.rr.unit)
        elif tip == "kurita":
            self.ev = VolumeRateUnit(self.air.evaporation_kurita() * (self.thot.c - self.tcold.c) * self.rr.value, self.rr.unit)
        else:
            self.ev = self.evaporation_thermo()
        return self.ev

    def set_cycles(self, cycles):
        self.cycles = cycles
        self.evaporation()
        self.mu = VolumeRateUnit(self.ev.value*cycles/(cycles-1), self.ev.unit)
        self.bd = VolumeRateUnit(self.mu.value/cycles, self.mu.unit)
        self.vol.unit = self.bd.volume.unit
        self.hti = TimeUnit(self.vol.value/self.bd.value*math.log(2), self.bd.time.unit)

    def efficacy(self):
        wb = self.air.wet_bulb_temp()
        self.eff = (self.thot.c - self.tcold.c)/(self.thot.c - wb.c)
        return self.eff

