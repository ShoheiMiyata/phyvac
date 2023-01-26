## pv.tdb2psat(tdb)
Function to calculate saturated water vapor pressure [kPa] from dry bulb temperature [&deg;C] 
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|tdb|float|Dry-bulb temperature[&deg;C]|
  
### returns:
Saturation vapor pressure[kPa]
  
## Sample codes
```
import phyvac as pv

print(pv.tdb2psat(30.0))
print(pv.tdb2psat(20.0))
print(pv.tdb2psat(10.0))
```
> Results  
> 4.248562967042921  
> 2.3406201212631594  
> 1.2289582804524475  
  
