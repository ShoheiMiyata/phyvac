## pv.tdb_rh2twb(tdb, rh)
乾球温度[&deg;C]と相対湿度[%]から湿球温度[&deg;C]を算出する関数    
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|tdb|float|乾球温度[&deg;C]|
|rh|float|相対湿度[%] (0.0~100.0)|
  
### returns:
湿球温度[&deg;C]
  
## サンプルコード  
```
import phyvac as pv

print(pv.tdb_rh2tdp(30.0, 60.0))
print(pv.tdb_rh2tdp(30.0, 40.0))
print(pv.tdb_rh2tdp(20.0, 40.0))
```
> 結果  
> 23.828125  
> 15.234375  
> 12.40234375  
  
