## pv.tdb_rh2h_x(tdb, rh)
乾球温度[&deg;C]と相対湿度[%]から比エンタルピーh[kJ/kg']と絶対湿度x[kg/kg']を算出する関数  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|tdb|float|乾球温度[&deg;C]|
|rh|float|相対湿度[%] (0.0~100.0)|
  
### returns:
[比エンタルピーh[kJ/kg'], 絶対湿度x[kg/kg']]
  
## サンプルコード  
```
import phyvac as pv

print(pv.tdb_rh2h_x(30.0, 60.0))
print(pv.tdb_rh2h_x(30.0, 40.0))
print(pv.tdb_rh2h_x(20.0, 40.0))
```
> 結果  
> [71.16747620490443, 0.016030771356736712]  
> [57.27223524658105, 0.010596149580170935]  
> [34.82281548353221, 0.005792615035667878]  
  

