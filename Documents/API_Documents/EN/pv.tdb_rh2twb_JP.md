## pv.tdb_rh2twb(tdb, rh)
Function to calculate wet bulb temperature [&deg;C] from dry bulb temperature [&deg;C] and relative humidity [%].
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|tdb|float|Dry Bulb Temperature[&deg;C]|
|rh|float|Relative humidity[%] (0.0~100.0)|
  
### returns:
Wet bulb temperature[&deg;C]
  
## Sample Codes  
```
import phyvac as pv

print(pv.tdb_rh2twb(30.0, 60.0))
print(pv.tdb_rh2twb(20.0, 60.0))
print(pv.tdb_rh2twb(20.0, 40.0))
```
> Results
> 23.828125  
> 15.234375  
> 12.40234375  
  
