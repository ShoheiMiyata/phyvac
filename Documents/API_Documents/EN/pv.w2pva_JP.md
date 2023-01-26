## pv.w2pva(w)
Function to calculate vapor pressure [kPa] from absolute humidity [kg/kg(DA)]   
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|w|float|Absolute humidity[kg/kg(DA)]|
  
### returns:
Steam pressure[kPa]
  
## Sample Codes 
```
import phyvac as pv

print(pv.w2pv(0.030))
print(pv.w2pv(0.020))
print(pv.w2pv(0.010))
```
> Results  
> 4.6621932515337425  
> 3.156542056074766  
> 1.603243670886076  
