## pv.tdb2psat(tdb)
乾球温度[&deg;C]から飽和水蒸気圧[kPa]を算出する関数    
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|tdb|float|乾球温度[&deg;C]|
  
### returns:
飽和水蒸気圧[kPa]
  
## サンプルコード  
```
import phyvac as pv

print(pv.tdb2psat(30.0))
print(pv.tdb2psat(20.0))
print(pv.tdb2psat(10.0))
```
> 結果  
> 4.248562967042921  
> 2.3406201212631594  
> 1.2289582804524475  
  
