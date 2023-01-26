## pv.tdb_w2h(tdb, w)
Function to calculate specific enthalpy [kJ/kg(DA)] from dry bulb temperature [&deg;C] and absolute humidity [kg/kg(DA)    
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|tdb|float|Dry Bulb Temperature[&deg;C]|
|w|float|Absolute humidity[kg/kg(DA)]|
  
### returns:
Specific enthalpy[kJ/kg(DA)]
  
## Sample Codes
```
import phyvac as pv

print(pv.tdb_w2h(30.0, 0.020))
print(pv.tdb_w2h(30.0, 0.010))
print(pv.tdb_w2h(20.0, 0.010))
```
> 結果  
> 81.316  
> 55.748000000000005  
> 45.501999999999995  
  
