## pv.tdb2hsat(tdb)
Function to calculate specific enthalpy of saturated water vapor pressure [kJ/kg(DA)] from dry bulb temperature [&deg;C]
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|tdb|float|Dry Bulb Temperature[&deg;C]|
  
### returns:
Specific enthalpy of saturated vapor pressure[kJ/kg(DA)]
  
## Sample Codes 
```
import phyvac as pv

print(pv.tdb2hsat(30.0))
print(pv.tdb2hsat(20.0))
print(pv.tdb2hsat(10.0))
```
> Results   
> 99.74893019859252  
> 57.42899040376426  
> 29.289372794883924  
