## pva2w(pva)
Function to calculate absolute humidity [kg/kg(DA)] from vapor pressure [kPa]
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|pva|float|Steam pressure[kPa]|
  
### returns:
Absolute humidity[kg/kg(DA)]
  
## Sample codes  
```
import phyvac as pv

print(pv.pva2w(5.0))
print(pv.pva2w(4.0))
print(pv.pva2w(3.0))
```
> Results  
> 0.032286529976641574  
> 0.025563832519907525  
> 0.018977879481311976  
