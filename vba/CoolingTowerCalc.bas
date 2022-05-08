Attribute VB_Name = "CoolingTowerCalc"
Function evaporation_snip(thot As Double, tcold As Double, tair As Double) As Double
    evaporation_snip = (0.0009971 + 0.00002357 * (tair) - 0.0000002143 * (tair)) * (thot - tcold)
End Function
Function evaporation_kurita(thot As Double, tcold As Double, tair As Double) As Double
    evaporation_kurita = (0.575 + 0.011 * tair) * (thot - tcold) / 580
End Function
Function pressure_of_saturated_vapor(temp As Double) As Double
  pressure_of_saturated_vapor = Exp((1500.3 + 23.5 * temp) / (234 + temp))
End Function
Function pressure_of_vapor(temp As Double, moist As Double)
  pressure_of_vapor = moist * pressure_of_saturated_vapor(temp)
End Function
Function content_of_water(temp As Double, moist As Double, pressure_of_air As Double)
 content_of_water = 622 * pressure_of_vapor(temp, moist) / (pressure_of_air - pressure_of_vapor(temp, moist))
End Function
Function heat_of_evaporasation(temp As Double) As Double
 heat_of_evaporasation = -2.362 * temp + 2501
End Function
Function enthalpy_wet_air(temp As Double, moist As Double, pressure_of_air As Double) As Double
   enthalpy_wet_air = 1.006 * temp + (heat_of_evaporasation(temp) + 1.86 * temp) * content_of_water(temp, moist, pressure_of_air) / 1000
End Function
Function wet_bulb_temp(temp As Double, moist As Double, pressure_of_air As Double) As Double
   Dim ent As Double
   ent = enthalpy_wet_air(temp, moist, pressure_of_air)
   wet_bulb_temp = (-6.14 + 0.651 * ent) / (1 + 0.0097 * ent - 0.00000312 * ent ^ 2)
End Function
Function lg_ratio(thot As Double, tcold As Double, tair As Double, moist As Double, pressure As Double) As Double
     ' mois as 0..1, air pressure as Pa
     ' calculated as full!!! equilibrium, i.e. temp of hot air is equal to temp of hot water and counter flow
     Dim delta_enthalpy_of_water, enthalpy_of_cold_air, enthalpy_of_hot_air As Double
     delta_enthalpy_of_water = 4.18 * (thot - tcold)
     enthalpy_cold_air = enthalpy_wet_air(tair, moist, pressure)
     enthalpy_hot_air = enthalpy_wet_air(thot, 1, pressure)
     lg_ratio = (enthalpy_hot_air - enthalpy_cold_air) / delta_enthalpy_of_water
End Function
Function evaporation(thot As Double, tcold As Double, tair As Double, moist As Double, pressure As Double) As Double
    Dim x, was_water, became_water As Double
    x = lg_ratio(thot, tcold, tair, moist, pressure)
    was_water = content_of_water(tair, moist, pressure)
    became_water = content_of_water(thot, 1, pressure)
    evaporation = (became_water - was_water) / x / 1000
End Function
