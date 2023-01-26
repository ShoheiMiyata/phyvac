## pv.tdb_rh2h_x(tdb, rh)
Function to calculate specific enthalpy h[kJ/kg'] and absolute humidity x[kg/kg'] from dry bulb temperature [&deg;C] and relative humidity [%].    
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|tdb|float|Dry-bulb temperature[&deg;C]|
|rh|float|Relative humidity[%] (0.0~100.0)|
  
### returns:
[Specific enthalpy h[kJ/kg'], Absolute humidity x[kg/kg']]
  
## Sample codes
```
import phyvac as pv

print(pv.tdb_rh2h_x(30.0, 60.0))
print(pv.tdb_rh2h_x(30.0, 40.0))
print(pv.tdb_rh2h_x(20.0, 40.0))
```
> Results
> [71.16747620490443, 0.016030771356736712]  
> [57.27223524658105, 0.010596149580170935]  
> [34.82281548353221, 0.005792615035667878]  
  

