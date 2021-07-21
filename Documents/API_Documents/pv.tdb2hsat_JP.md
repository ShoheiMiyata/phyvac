## pv.tdb2hsat(tdb, rh)
乾球温度[&deg;C]から飽和水蒸気圧の比エンタルピー[kJ/kg(DA)]を算出する関数    
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|tdb|float|乾球温度[&deg;C]|
  
### returns:
飽和水蒸気圧の比エンタルピー[kJ/kg(DA)]
  
## サンプルコード  
```
import phyvac as pv

print(pv.tdb2hsat(30.0))
print(pv.tdb2hsat(20.0))
print(pv.tdb2hsat(10.0))
```
> 結果  
> 99.74893019859252  
> 57.42899040376426  
> 29.289372794883924  
