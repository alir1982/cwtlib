import math
import numpy as np
from copy import deepcopy
import requests
import os
import pathlib
import sys
path = pathlib.Path(__file__).parent
sys.path.append(str(path))
from measure_units import *

try:
    TOKEN = os.environ["OpenWeatherMap"]
except:
    TOKEN = None

class Air:
    '''
    Передаем температуру, влажность и давление
    '''
    class_name = "air"
    def __init__(self, *args):
        for v in args:
            if isinstance(v, TempUnit):
                self.tair = v
            elif isinstance(v, HumidityUnit):
                self.hair = v
            elif isinstance(v, PressureUnit):
                self.pair = v
            else:
                raise Exception('Некорректный тип значение')

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
        a = np.log(self.hair.ratio) + 17.62 * self.tair.c / (243.12 + self.tair.c)
        dt = 243.12 * a / (17.62 - a)
        return TempUnit(dt, "c")

    def dew_temp(self):
        wb = self.tair.c * np.arctan(0.151977 * (self.hair.ratio + 8.313659) ** 0.5) + \
             np.arctan(self.tair.c + self.hair.ratio) - np.arctan(self.hair.ratio - 1.676331) + \
             0.00391838 * self.hair.ratio ** 1.5 * np.arctan(0.023101 * self.hair.ratio) - 4.686035
        return TempUnit(wb, "c")

    
    def __str__(self):
        return f"Tair={self.tair.c} C Hair={self.hair.proc} % Pair={self.pair.hg} Hg"


class Tower:
    def __init__(self, *args):
        temps = []
        for v in args:
            if isinstance(v, TempUnit):
                temps.append(v)
            elif isinstance(v, Air):
                self.air = v
            elif isinstance(v, VolumeUnit):
                self.v = v
            elif isinstance(v, VolumeRateUnit):
                self.rr = v
            else:
                raise Exception("tower_init_error")
        if temps[0] > temps[1]:
            self.thot, self.tcold = temps
        else:
            self.cold, self.thot = temps
    
    def __str__(self):
        return f"V={self.v.m3} RR={self.v.value} {self.v.unit} THOT={self.thot.c} C TCOLD={self.tcold.c} C AIR={self.air}"

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
        self.v.unit = self.bd.volume.unit
        self.hti = TimeUnit(self.v.value/self.bd.value*math.log(2), self.bd.time.unit)

    def efficacy(self):
        wb = self.air.wet_bulb_temp()
        self.eff = (self.thot.c - self.tcold.c)/(self.thot.c - wb.c)
        return self.eff

