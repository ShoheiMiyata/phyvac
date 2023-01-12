## pv.w2pva(w)
絶対湿度[kg/kg(DA)]から蒸気圧[kPa]を算出する関数    
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|w|float|絶対湿度[kg/kg(DA)]|
  
### returns:
蒸気圧[kPa]
  
## サンプルコード  
```
import phyvac as pv

print(pv.w2pv(0.030))
print(pv.w2pv(0.020))
print(pv.w2pv(0.010))
```
> 結果  
> 4.6621932515337425  
> 3.156542056074766  
> 1.603243670886076  
