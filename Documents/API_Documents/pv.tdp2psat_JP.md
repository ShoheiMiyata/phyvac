## tdp2psat(tdp)
露点温度[&deg;C]から飽和水蒸気圧[kPa]を算出する関数    
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|tdp|float|露点温度[&deg;C]|
  
### returns:
飽和水蒸気圧[kPa]
  
## サンプルコード  
```
import phyvac as pv

print(pv.tdp2psat(20.0))
print(pv.tdp2psat(10.0))
print(pv.tdp2psat(5.0))
```
> 結果  
> 2.3392148103968
> 1.2281838951501882
> 0.8725748806674649  
