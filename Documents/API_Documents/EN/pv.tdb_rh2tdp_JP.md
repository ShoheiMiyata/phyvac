## pv.tdb_rh2tdp(tdb, rh)
Function to calculate dew point temperature [&deg;C] from dry bulb temperature [&deg;C] and relative humidity [%].   
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|tdb|float|Dry-bulb temperature[&deg;C]|
|rh|float|Relative humidity[%] (0.0~100.0)|
  
### returns:
Dew point temperature[&deg;C]
  
## Sample codes
```
import phyvac as pv

print(pv.tdb_rh2tdp(30.0, 60.0))
print(pv.tdb_rh2tdp(30.0, 40.0))
print(pv.tdb_rh2tdp(20.0, 40.0))
```
> Results  
> 21.3818359375  
> 14.9365234375  
> 6.015625  
  

