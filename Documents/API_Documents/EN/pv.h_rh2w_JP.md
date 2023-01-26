## h_rh2w(h, rh)
Function to calculate absolute humidity [kg/kg(DA)] from specific enthalpy [kJ/kg(DA)] and relative humidity [%] 
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|h|float|Specific enthalpy[kJ/kg(DA)]|
|rh|float|Relative humidity[%] (0.0~100.0)|
  
### returns:
Absolute humidity[kg/kg(DA)]
  
## Sample Codes  
```
import phyvac as pv

print(pv.h_rh2w(80.0, 60.0))
print(pv.h_rh2w(60.0, 60.0))
print(pv.h_rh2w(60.0, 40.0))
```
> Results  
> 0.018497851092694938  
> 0.013060151350983672  
> 0.01125538220175783  
