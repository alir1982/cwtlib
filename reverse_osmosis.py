import numpy as np
import sys
import pathlib
path = pathlib.Path(__file__).parent
sys.path.append(str(path))
from measure_units import Ion, TempUnit, TDSUnit, PressureUnit, AreaUnit


class Flow:
    def __init__(self, rate, pressure, temp=None, tds=None):
        self.temp = temp
        self.rate = rate
        self.pressure = pressure
        self.tds = tds

class RO:

    use_pol_factor = True
    tcf_less_25   = 3020
    tcf_bigger_25 = 2640
    area = AreaUnit(1, "m2")

    def __init__(self, feed, permeate, concentrate):
        self.feed = feed
        self.permeate = permeate
        self.concentrate = concentrate

    @property
    def concentrate_factor(self):
        return (self.permeate.rate.m3_hour + self.concentrate.rate.m3_hour)/self.concentrate.rate.m3_hour

    @property
    def set_concentrate_tds(self):
        self.concentrate.tds = self.feed.tds*self.concentrate_factor

    @property
    def average_net_driving_pressure(self):
        andp = self.feed.pressure.psi + self.concentrate.pressure.psi
        andp /= 2
        andp -= self.feed.tds.__tds*(1+self.concentrate_factor)/200
        andp -= self.permeate.pressure.psi
        return PressureUnit(andp, "psi")

    @property
    def salt_rejection(self):
        return 1 - self.permeate.tds.__tds/self.feed.tds.__tds

    @property
    def salt_passage(self):
        return 1 - self.salt_rejection

    @property
    def recovery(self):
        return self.permeate.rate.m3_hour/self.feed.rate.m3_hour

    @property
    def beta(self):
        if self.use_pol_factor:
            return np.exp(0.75 * 2 * self.recovery/(2-self.recovery))**(1 / 8)
        else:
            return 1

    @property
    def temperature_correction_factor(self):
        if self.feed.temp.c > 25:
            return np.exp(self.tcf_bigger_25 * (1/298 - 1/self.feed.temp.k))
        else:
            return np.exp(self.tcf_less_25 * (1/298 - 1/self.feed.temp.k))

    @property
    def average_feed_concentrate_concentration_factor(self):
        return np.log(1/(1 - self.recovery))/self.recovery

    @property
    def average_feed_concentrate_concentration(self):
        return self.feed.tds.__tds*self.average_feed_concentrate_concentration_factor*self.beta

    @property
    def average_feed_concentrate_osmotic_pressure(self):
        return 0.0385 * self.average_feed_concentrate_concentration * self.feed.temp.k / \
               (1000 - self.average_feed_concentrate_concentration) / 14.5038

    @property
    def permeate_osmotic_pressure(self):
        return 0.0385 * self.permeate.tds.__tds * self.feed.temp.k / (1000 - self.permeate.tds.__tds / 1000) / 14.5038

    @property
    def diff_pressure(self):
        return self.feed.pressure.bar - self.concentrate.pressure.bar

    @property
    def ndp(self):
        return self.feed.pressure.bar - self.diff_pressure/2 - self.average_feed_concentrate_osmotic_pressure +\
               self.permeate_osmotic_pressure - self.permeate.pressure.bar

    @property
    def water_mass_transfer_coeff(self):
        return self.permeate.rate.m3_hour/self.area.m2/self.temperature_correction_factor/self.ndp

    @property
    def salt_mass_transfer_coeff(self):
        return self.permeate.tds.__tds * self.permeate.rate.m3_hour/ self.area.m2 / self.temperature_correction_factor / self.average_feed_concentrate_concentration

    @property
    def norm_permeate_flow(self, ro_zero):
        return self.permeate.rate.m3_hour*ro_zero.average_net_driving_pressure.bar/self.average_net_driving_pressure.bar*ro_zero.temperature_correction_factor/self.temperature_correction_factor

    @property
    def norm_salt_rejection(self, ro_zero):
        return 1 - self.salt_passage*self.permeate.rate.m3_hour/ro_zero.permeate.rate.m3_hour*self.temperature_correction_factor

    @property
    def norm_pressure_drop(self, ro_zero):
        return self.diff_pressure*ro_zero.permeate.rate.m3_hour/self.permeate.rate.m3_hour





