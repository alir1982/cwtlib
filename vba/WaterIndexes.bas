Attribute VB_Name = "WaterIndexes"
Function na(hrd As Double, cl As Double, so4 As Double, alk As Double, po4 As Double) As Double
  Dim cations, anions As Double
  cations = hrd
  anions = so4 / 48 + cl / 35.5 + alk + po4 / 32
  na = anions - cations
End Function
Function Log10(a As Double) As Double
    Log10 = Log(a) / Log(10)
End Function
Function phs(tds As Double, temp As Double, ca As Double, alk As Double) As Double
   'tds mg/l, temp C, ca meq/l, alk meq/l
   Dim a, b, c, d As Double
   a = (Log10(tds) - 1) / 10
   b = -13.12 * Log10(temp + 273.15) + 34.55
   c = Log10(ca * 50) - 0.4
   d = Log10(alk * 50)
   phs = 9.3 + a + b - c - d
End Function
Function phs_po4(ca As Double, po4 As Double, temp As Double) As Double
'ca as meq/l  po4 as mg/l, temp as C+
    phs_po4 = (11.75 - Log10(ca * 50) - Log10(po4) - 2 * Log10(temp)) / 0.65
End Function
Function modified_larson_index(hrd As Double, alk As Double, cl As Double, so4 As Double, po4 As Double, hti As Double, temp As Double)
'hti days!
    modified_larson_index = (cl / 35.5 * 50 + so4 / 48 * 50 + na(hrd, cl, so4, alk, po4) * 50) ^ 0.5 * temp / 25 * hti / alk / 50
End Function
