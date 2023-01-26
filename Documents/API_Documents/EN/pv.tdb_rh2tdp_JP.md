## pv.tdb_rh2tdp(tdb, rh)
Function to calculate dew point temperature [&deg;C] from dry bulb temperature [&deg;C] and relative humidity [%].   
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|tdb|float|乾球温度[&deg;C]|
|rh|float|相対湿度[%] (0.0~100.0)|
  
### returns:
露点温度[&deg;C]
  
## サンプルコード  
```
import phyvac as pv

print(pv.tdb_rh2tdp(30.0, 60.0))
print(pv.tdb_rh2tdp(30.0, 40.0))
print(pv.tdb_rh2tdp(20.0, 40.0))
```
> 結果  
> 21.3818359375  
> 14.9365234375  
> 6.015625  
  

