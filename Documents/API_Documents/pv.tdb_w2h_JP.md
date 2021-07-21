## pv.tdb_w2h(tdb, w)
乾球温度[&deg;C]と絶対湿度[kg/kg(DA)]から比エンタルピー[kJ/kg(DA)]を算出する関数    
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|tdb|float|乾球温度[&deg;C]|
|w|float|絶対湿度[kg/kg(DA)]|
  
### returns:
比エンタルピー[kJ/kg(DA)]
  
## サンプルコード  
```
import phyvac as pv

print(pv.tdb_w2h(30.0, 0.020))
print(pv.tdb_w2h(30.0, 0.010))
print(pv.tdb_w2h(20.0, 0.010))
```
> 結果  
> 81.316  
> 55.748000000000005  
> 45.501999999999995  
  
