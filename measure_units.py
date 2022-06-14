import copy
import numpy as np

class MeasureUnit:
    '''
        Базовый класс для описания единиц измерения в дочерних классах переопределяется словарь units (аттрибут класса)
        В этом словаре ключ - название единицы измерения, а значение может быть либо в виде списка либо в виде числового значения.
        Числовое значение показывает сколько единиц содержится в базовой единице измерения (например, если базовая единица измерения грамм, то для мг
        значение будет 1000)
        Список состоит из двух элементов: 1) Коэффициент; 2) Смещение. Например, если базовая величина градус цельсия, то для кельвинов
        коэффициент - 1 (в 1 цельсии 1 кельвин), а смещение составит 273.15
        Для базовой величины коэффициент равен 1 а смещение (если применимо) 0
    '''
    units = {"simple":[1, 0], "complex":[2, 10]}
    def __init__(self, v, u):
        self.unit = u
        self._get_koeff()
        self.value = v   
        if self.a == 0 :
            raise ValueError("Коэффициент не должен равняться 0, проверьте массив units")
    
    def __getattr__(self, name):
        if name.startswith("__") or name in self.__dict__.keys():
            return self.__getattribute__(name)
        if name in self.units.keys():
            self.unit = name
            return self.value
        else:
            raise AttributeError(f"{name} Неправильное название ЕИ")

    def __setattr__(self, name, value):
        if name in self.units.keys():
            self.unit = name
            self.value = value
        super().__setattr__(name, value)
    
    def __cmp__(self, value):
        if self._value > value._value:
            return 1
        elif self._value == value._value:
            return 0
        else:
            return -1
    
    def __gt__(self, value):
        if self._value > value._value:
            return True
        else:
            return False
    
    def __ls__(self, value):
        if self._value < value._value:
            return True
        else:
            return False


    @property
    def i_value(self):
        return self._value

    @property
    def unit(self):
        return self._unit
    
    def _get_koeff(self):
        flag_temp_like = type(self.units[list(self.units.keys())[0]]) in [list, tuple]
        if flag_temp_like:
            a = self.units[self.unit][0]
            b = self.units[self.unit][1]
        else:
            a = self.units[self.unit]
            b = 0
        self.a, self.b = a, b


    @property
    def value(self):
        return self._value * self.a + self.b
    
    @unit.setter
    def unit(self, u):
        if u in self.units.keys():
            self._unit = u
            self._get_koeff()
        else:
            raise Exception(f"{u} {type(self)} - неправильная единица измерения")
    
    @value.setter
    def value(self, v):
        self._value = (v - self.b)/self.a
    
    def __add__(self, other):
        ans = copy.copy(self)
        if type(other) == type(self):
            ans._value = self._value  + other.i_value
            return ans
        else:
            try:
                ans.value = self.value + other
                return ans
            except:
                raise Exception("MeasureUnits.__add__ problem with add value")

    def __mul__(self, other):
        ans = copy.copy(self)
        try:
            ans._value = self._value * other
            return ans
        except:
            raise Exception("MeasureUnits.__mul__ problem with add value")
    
    def __truediv__(self, other):
        ans = copy.copy(self)

        try:
            ans._value = self._value / other
            return ans
        except:
            raise Exception("MeasureUnits.__truediv__ problem with add value")
    
    def __sub__(self, other):
        ans = copy.copy(self)
        try:
            ans._value -= other
            return ans
        except:
            raise Exception("MeasureUnits.__sub__ problem with add value")


class TempUnit(MeasureUnit):
    class_name = "temp_unit"
    name = "temp"
    units = {
        "c" : (1, 0),
        "k" : (1, 273.15),
        "f" : (1.8, 32)
    }


class VolumeRateUnit(MeasureUnit):
    class_name = "volume_rate_unit"
    name="volume_rate"

    def __init__(self, value, unit):
        if "/" in unit:
            unit = unit.replace("/", "_")
        self.volume = VolumeUnit(value, unit.split("_")[0])
        self.time = TimeUnit(1, unit.split("_")[1])

    def __getattr__(self, item):
        if "_" in item and item not in self.__dict__.keys():
            self.volume.unit = item.split("_")[0]
            self.time.unit = item.split("_")[1]
            return self.volume.value / self.time.value
        else:
            return super().__getattribute__(item)
    
    def __setattr__(self, key, value):
        if "_" in key and key not in self.__dict__.keys():
            volume_unit = key.split("_")[0]
            time_unit = key.split("_")[1]
            self.volume.__setattr__(volume_unit, value)
            self.time.__setattr__(time_unit, 1)
        else:
            super().__setattr__(key, value)


    @property
    def value(self):
        return self.volume.value/self.time.value

    @value.setter
    def value(self, v):
        self.volume.value = v
        self.time.value = 1

    @property
    def unit(self):
        return f"{self.volume.unit}/{self.time.unit}"

    @unit.setter
    def unit(self, u):
        if "/" in u:
            u = u.replace("/", "_")
        v, t = u.split("_")
        self.volume.unit = v
        self.time.unit = t

    def __add__(self, other):
        from copy import deepcopy
        if isinstance(other, VolumeRateUnit):
            _prev_unit = other.unit
            other.unit = self.unit
            ans = VolumeRateUnit(self.value, self.unit)
            ans.value += other.value
            other.unit = _prev_unit
            return ans
        else:
            try:
                self.value += other
                return self
            except:
                raise Exception("VolumeRateUnit.__add__ problem with add value")

    def __mul__(self, other):
        try:
            self.value *= other
            return self
        except:
            raise Exception("VolumeRateUnit.__mul__ problem with add value")

    def __truediv__(self, other):
        try:
            self.value /= other
            return self
        except:
            raise Exception("VolumeRateUnit.__truediv__ problem with add value")


class TimeUnit(MeasureUnit):
    class_name = "time_unit"
    name = "time"
    units = dict(
        sec=1,
        min=1/60,
        hour=1/3600,
        day=1/3600/24,
        month=1/3600/24/30.5,
        week=1/3600/24/7,
        year=1/365/24/3600
    )

class LengthUnit(MeasureUnit):
    class_name = "length_unit"
    name ="length"
    units = {"cm" : 1, "m" : 0.01, "mm" : 10, "inches":1/2.54}

class AreaUnit(MeasureUnit):
    class_name = "area_unit"
    name = "area"
    units = dict(cm2=1, m2=0.0001, mm2=100)

class VolumeUnit(MeasureUnit):
    class_name = "volume_unit"
    name="volume"
    units = {"l": 1, "m3": 0.001, "cm3": 1000, "gal": 1/0.473/8, "pinta": 1/0.473, "barrel": 1/0.473/31.5/8}


class WeightUnit(MeasureUnit):
    class_name = "weight_unit"
    name="weight"
    units = {"kg": 1,"g": 1000,"mg": 1000000, "ounce":1/0.02835, "lb":1/0.4536}


class HeatUnit(MeasureUnit):
    class_name = "heat_unit"
    name="heat"
    units = {"kj": 1, "kcal": 0.238845889, "btu": 0.000948, "j":1000}


class PowerUnit(MeasureUnit):
    class_name = "power_unit"
    name="power"
    units = {"kw":1, "mw":1/1000, "kcalh": 859.845228, "btuh": 3414.424784, "w":1000}


class PressureUnit(MeasureUnit):
    class_name = "pressure_unit"
    name="pressure"
    units = {"kpa":1, "hpa":10, "atm":1/101.325, "psi":0.145, "bar": 0.01, "hg" : 760/101.325, "water":9800/101.325, "pa":1000}


class HumidityUnit(MeasureUnit):
    class_name = "humidity_unit"
    name="humidity"
    units = {"proc":100, "ratio":1}


class TDSUnit(MeasureUnit):
    class_name = "tds_unit"
    name= "tds"
    units = {"usm":1, "ppm":0.5}

    def __getattr__(self, item):
        if "tds" in item:
            return self.__tds()
        else:
            return super().__getattr__(item)

    def __tds(self):
        if self.usm > 100000:
            raise Exception("Conductivity is too high")
        elif self.usm > 7630:
            return 0.0000000000801 * np.exp((-50.6458 - np.log(self.usm))** 2 / 112.484)
        else:
            return 7.7E-20 * np.exp((-90.4756 - np.log(self.usm))**2 / 188.884)


class Ion(MeasureUnit):
    class_name = "ion_unit"
    ions = {
        "cl" : (35.5, 1, -1),
        "so4" : (96, 2, -1),
        "po4": (95, 3, -1),
        "fe" : (56, 2, 1),
        "ca" : (40, 2, 1),
        "mg" : (24, 2, 1),
        "na" : (23, 1, 1), 
        "no3": (62, 1, -1),
        "hco3" : (61, 1, -1),
        "hrd" : (40, 2, 1), 
        "alk" : (61, 1, -1),
        "sio2": (60, 2, -1),
        "na": (23, 1, 1),
        "k": (39, 1, 1)
    }
    
    def __init__(self, name, value, unit):
        self.name = name
        super().__init__(value, unit)
    
    def is_cation(self):
        return (self.ions[self.name][2]==1)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self.units = {}
        self.units["mmol"] = 1
        self.units["caco3"] = 50 * self.ions[self.name][1] 
        self.units["meq"] = self.ions[self.name][1]
        self.units["ppm"] = self.ions[self.name][0]
        self.units["mol"] = 0.001
        self.units["eq"] = self.ions[self.name][1]*0.001

    def molar_weight(self):
        return self.ions[self.name][0]
    
    def equiv_weight(self):
        return self.molar()/self.ions[self.name][1]

    def activity(self, ion_strength):
        z = self.charge
        log_f = -(0.511 * ion_strength ** 0.5 / (1 + 1.5 * ion_strength ** 0.5) - 0.2 * ion_strength) * z ** 2
        return 10 ** log_f * self.mol

    @property
    def charge(self):
        return self.ions[self.name][2]*self.ions[self.name][1]
    
    def __add__(self, other):
        ans = Ion(self.name, self.value, self.unit)
        if type(other) == Ion:
            if other.name == self.name:
                ans._value = self._value + other._value
            elif other.name in ["ca", "mg"] and self.name in ["ca", "mg"]:
                ans._value = self._value + other._value
                ans.name = "hrd"
            else:
                raise Exception("Нельзя складывать концентрации разных ионов")
            return ans
        else:
            try:
                ans.value = self.value + other
                return ans
            except:
                raise Exception("Ion.__add__ problem with add value")
    
    def __sub__(self, other):
        ans = Ion(self.name, self.value, self.unit)
        if type(other) == Ion:
            if other.name == self.name:
                ans._value = self._value - other._value
            elif other.name=="ca" and self.name == "hrd":
                ans._value = self._value - other._value
                ans.name = "mg"
            elif other.name =="mg" and self.name == "hrd":
                ans._value = self._value - other._value
                ans.name = "ca"                
            else:
                raise Exception("Нельзя вычитать концентрации разных ионов")
            return ans
        else:
            try:
                ans.value = self.value + other
                return ans
            except:
                raise Exception("VolumeRateUnit.__sub__ problem with add value")

    
