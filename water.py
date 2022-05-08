import numpy as np
import copy
from measure_units import Ion, TempUnit, TDSUnit
import sys
import pathlib
path = pathlib.Path(__file__).parent
sys.path.append(str(path))

class Water:
    '''
    В конструктор передается температура, рН электропроводность, жесткость, щелочность и прочие параметры воды. рН передается в виде float или int (необязательный)
    параметр. Жесткость или кальций, щелочность и электропроводность, температура - обязательные параметры
    '''
    def __init__(self, ph, *args, **kwargs):
        self.__dict__["ph"] = ph
        self.__setattr__("cycles", 1)
        try:
            for v in args:
                if type(v) in [Ion, TempUnit, TDSUnit]:
                    self.__setattr__(v.name, v)
            self.set_hrd()
            self.check_is_minimally_enough()
        except Exception as e:
            raise Exception("Результат анализа неверен!")
    
    def set_ion(self, i):
        self.__dict__[i.name] = i

    def check_is_minimally_enough(self):
        for n in ["alk", "ca", "temp", "tds"]:
            if not n in self.__dict__.keys():
                raise Exception(f"{n} has to be set")    

    def set_hrd(self):
        rank = ("hrd" in self.__dict__.keys())*4 + ("ca" in self.__dict__.keys())*2 + ("mg" in self.__dict__.keys())*1
        if rank == 7:
            pass
        elif rank == 6:
            self.mg = self.hrd - self.ca
        elif rank == 5:
            self.ca = self.hrd - self.mg
        elif rank == 4:
            self.ca = self.hrd * 3/4
            self.ca.name = "ca"
            self.mg = self.hrd  - self.ca
        elif rank == 3:
            self.hrd = self.ca + self.mg
        elif rank == 2:
            self.mg = self.ca / 3
            self.mg.name = "mg"
            self.hrd = self.mg + self.ca
        elif rank == 1:
            self.ca = self.mg * 3
            self.ca.name = "ca"
            self.hrd = self.ca  + self.mg
        else:
            raise Exception("Установите жесткость или кальций или магний")

    def set_cycles(self, c):
        c_old = self.cycles
        self.cycles = c
        for k, v in self.__dict__.items():
            if type(v) in [Ion, TDSUnit]:
                self.__dict__[k] *= c/c_old
        self.ph = self.ph_predict()

    def ph_predict(self, a=4.17, b=1.7177):
        return a + b * np.log10(self.alk.caco3)

    def phs(self):
        return self.pk2() - self.pks() - np.log10(self.ca.mol) + self.phco3() + 5 * self.pfm()

    def pk2(self):
        return 107.8871 + 0.03252849 * self.temp.k - 5151.79 /self.temp.k  - 38.92561 * np.log10(self.temp.k) + 563713.9 / self.temp.k ** 2

    def pks(self):
        return 171.9065 + 0.077993 * self.temp.k - 2839.319/self.temp.k- 71.595 * np.log10(self.temp.k)

    def pkw(self):
        return 4471/self.temp.k  + 0.01706 * self.temp.k - 6.0875

    def phco3(self):
        ans = self.alk.mol + 10 ** (self.pfm() - self.ph) - 10 ** (self.ph + self.pfm() - self.pkw())
        ans /= 1 + 0.5 * 10 ** (self.ph - self.pk2())
        return -np.log10(ans)

    def pfm(self):
        return 1.82E6 * (self.e_help() * self.temp.k) ** (-1.5) * (self.ionic_strength() ** 0.5 / (1 + self.ionic_strength() ** 0.5) - 0.3 * self.ionic_strength() ** 0.5)

    def e_help(self):
        return 60954.0 / (self.temp.k + 116) - 68.937

    def ionic_strength(self):
        return 1.6E-5 * self.tds.ppm

    def casi(self):
        ca0 = self.ca.mol
        if self.phs() >= self.ph:
            return 1
        while self.phs() < self.ph:
            self.ca.mol -= 0.01
        ca1 = self.ca.mol
        self.ca.mol = ca0
        return ca0 / ca1

    def ccsp(self):
        ca0 = self.ca.meq
        alk0 = self.alk.meq
        if self.phs() > self.ph:
            return 1
        while self.phs() < self.ph:
            self.ca.meq = self.ca.meq - 0.01
            self.alk.meq = self.alk.meq - 0.01
        ca1 = self.ca.meq
        self.ca.meq = ca0
        self.alk.meq = alk0
        return ca0/ca1

    def lsi(self):
        return self.ph - self.phs()

    def rzn(self):
        return 2*self.phs() - self.ph

    def larsen(self):
        return 100*(self.cl.meq + self.so4.meq)/self.alk.meq
    
    def calc_ions(self):
        self.anions = 0 
        self.cations = 0
        for k, v in self.__dict__.items():
            if type(self.__dict__[k]) == Ion:
                if v.is_cation():
                    self.cations += v.caco3
                else:
                    self.anions += v.caco3
        self.cations -= self.hrd.caco3

    def calc_tds(self):
        self.calc_ions()
        tds = max(self.anions, self.cations)
        return TDSUnit(tds, "ppm")

    def calc_na(self):
        self.calc_ions()
        na =self.anions - self.cations
        if na > 0:
            return Ion("na", na, "caco3")
        else:
            return Ion("na", 0, "caco3")

    def larsen_modified(self, hti):
        '''Уточнить'''
        return (self.cl.meq + self.so4.meq + self.calc_na())**0.5/self.alk.meq*self.temp/25*hti/50/24

    def po4_si(self):
        return self.ph - (11.75 - np.log10(self.ca.caco3) - np.log10(self.po4.ppm) - 2 * np.log10(self.temp.c))/0.65

    def sio2_si(self):
        sio2_max = 21.43*self.ph - 4.3
        return self.sio2.ppm/sio2_max

    def caso4_si(self):
        return self.ca.ppm*self.so4.ppm/50000

    def phs_simple(self):
        a = (np.log10(self.tds.ppm)-1)/10
        b = -13.12*np.log10(self.temp.k) + 34.55
        c = np.log10(self.ca.caco3) - 0.4
        d = np.log10(self.alk.caco3)
        return 9.3 + a + b - c - d

    def lsi_simple(self):
        return self.ph - self.phs_simple()

    def rzn_simple(self):
        return 2*self.phs_simple() - self.ph
    
    def mix(self, other, other_ratio):
        if type(other) == Water:
            ans = copy.copy(self)
            ans.temp = self.temp*(1-other_ratio) + other.temp*other_ratio
            ans.tds = self.tds*(1-other_ratio) + other.tds*other_ratio
            for k in self.__dict__.keys():
                ans.__dict__[k] = self.__dict__[k] * (1-other_ratio) + other.__dict__[k] * other_ratio
            return ans
        else:
            raise Exception("не надо так складывать!")

