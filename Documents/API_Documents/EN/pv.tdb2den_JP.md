## tdb2den(tdb)
乾球温度[&deg;C]から密度[kg/m<sup>3</sup>]を算出する関数    
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|tdb|float|乾球温度[&deg;C]|
  
### returns:
密度[kg/m<sup>3</sup>]
  
## サンプルコード  
```
import phyvac as pv

print(pv.tdb2den(30.0))
print(pv.tdb2den(20.0))
print(pv.tdb2den(10.0))
```
> 結果  
> 1.1654910949868074  
> 1.2052418144611186  
> 1.2477997881355931  
