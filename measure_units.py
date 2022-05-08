import copy
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
            return super(MeasureUnit, self).__getattribute__(name)
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
        elif type(other) in [int, float]:
            ans.value = self.value + other
            return ans
        else:
            raise TypeError
    
    def __mul__(self, other):
        ans = copy.copy(self)
        if type(other) in [int, float]:
            ans._value = self._value * other
            return ans
        else:
            raise TypeError
    
    def __truediv__(self, other):
        ans = copy.copy(self)

        if type(other) in [int, float]:
            ans._value = self._value / other
            return ans
        if type(other).__base__ == type(self).__base__:
            return self.value/other.value

        else:
            raise TypeError
    
    def __sub__(self, other):
        ans = copy.copy(self)
        if type(other) in [int, float]:
            ans._value -= other
            return ans
        else:
            raise TypeError



class TempUnit(MeasureUnit):
    name = "temp"
    units = {
        "c" : (1, 0),
        "k" : (1, 273.15),
        "f" : (1.8, 32)
    }

class VolumeRateUnit(MeasureUnit):
    name="volume_rate"
    units = dict(
        gpd=["gal", "day"],
        mph=["m3", "hour"]
    )
    def __init__(self, v, unit):
        vol_unit, time_unit = unit.split("/")
        self.volume = VolumeUnit(v, vol_unit)
        self.time = TimeUnit(1, time_unit)

    def __getattr__(self, item):
        if item in self.units.keys():
            v, t = self.units[item]
            self.unit = f"{v}/{t}"
            return self.value
        else:
            return super(VolumeRateUnit, self).__getattr__(item)
    
    def __setattr__(self, key, value):
        if key in self.units.keys():
            v, t = self.units[key]
            self.unit = f"{v}/{t}"
            self.value = value
        else:
            return super(VolumeRateUnit, self).__setattr__(key, value)

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
        v, t = u.split("/")
        self.volume.unit = v
        self.time.unit = t

    def __add__(self, other):
        if type(other) in [int, float]:
            self.value += other
            return self
        else:
            raise Exception("only int or float for VolumeRate + ")

    def __mul__(self, other):
        if type(other) in [int, float]:
            self.value *= other
            return self
        else:
            raise Exception("only int or float for VolumeRate * ")

    def __truediv__(self, other):
        if type(other) in [int, float]:
            self.value /= other
            return self
        else:
            raise Exception("only int or float for VolumeRate /")


class TimeUnit(MeasureUnit):
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
    name="length"
    units = {"cm" : 1, "m" : 0.01, "mm" : 10, "inches":1/2.54}


class VolumeUnit(MeasureUnit):
    name="volume"
    units = {"l":1, "m3":0.001,"cm3":1000,"gal": 1/0.473/8,"pinta":1/0.473,"barrel":1/0.473/31.5/8}


class WeightUnit(MeasureUnit):
    name="weight"
    units = {"kg": 1,"g": 1000,"mg": 1000000, "ounce":1/0.02835, "lb":1/0.4536}


class HeatUnit(MeasureUnit):
    name="heat"
    units = {"kj": 1, "kcal": 0.238845889, "btu": 0.000948, "j":1000}


class PowerUnit(MeasureUnit):
    name="power"
    units = {"kw":1, "mw":1/1000, "kcalh": 859.845228, "btuh": 3414.424784, "w":1000}


class PressureUnit(MeasureUnit):
    name="pressure"
    units = {"kpa":1, "hpa":10, "atm":1/101.325, "psi":0.145, "bar": 0.01, "hg" : 760/101.325, "water":9800/101.325, "pa":1000}


class HumidityUnit(MeasureUnit):
    name="humidity"
    units = {"proc":100, "ratio":1}


class TDSUnit(MeasureUnit):
    name= "tds"
    units = {"usm":2, "ppm":1}


class Ion(MeasureUnit):
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

    def molar_weight(self):
        return self.ions[self.name][0]
    
    def equiv_weight(self):
        return self.molar()/self.ions[self.name][1]
    
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
        elif type(other) in [int, float]:
            ans.value = self.value + other
            return ans
        else:
            raise Exception("Складывать можно только с числом или другим объектом класса Ion")
    
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
        elif type(other) in [int, float]:
            ans.value = self.value + other
            return ans
        else:
            raise Exception("Складывать можно только с числом или другим объектом класса Ion")
    