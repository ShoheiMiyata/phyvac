## pv.Fan(pg=[948.66, -0.5041, -0.097], eg=[0.0773, 0.0142, -1.00e-04], r_ef=0.6)
Characteristics of fans and calculation of electricity consumption
<img src="https://user-images.githubusercontent.com/27459538/112824603-b2f09380-90c5-11eb-8e10-45acdd9ef187.png" width=40%>
  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|pg|list|Coefficient of pressure-flow rate (pg) curve [slicing, primary, secondary]|
|eg|list|Coefficient of efficiency-flow rate (eg) curve [slicing, primary, secondary]|
|inv|float|Inverter frequency ratio(min:0.0~max:1.0)|
|dp|float|fan lift [Pa]|
|g|float|Flow rate[m3/min]|
|pw|float|Electricity consumption[kW]|
|ef|float|Efficiency(0.0~1.0)|
|flag|float|1 if there is a problem in the calculation, 0 if there is not.|
  
## pv.Fan.f2p(g)
Calculate fan lift by g
  
### returns:
Fan lift dp
  
## pv.Fan.f2p_co()
Output the coefficient of the function of flow rate that represent fan lift
  
### returns:
List [slicing, primary, secondary]
  
## pv.Pump.cal()
Calculate the electricity consumption
  
### returns:
Electricity consumption pw
  
  
## Sample codes
```
import phyvac as pv

SA1 = pv.Fan() # Definition of SA1 (default values are used for parameters)
SA1.inv = 0.8 # Input inv
SA1.f2p(g=1.5) # Calculate the fan's lift when inv = 0.8 and flow rate = 1.5
SA1.cal() # Calculate the electricity consumption under the conditions above

print(SA1.g, SA1.dp, SA1.pw)
```
> Result  
> 1.5 0.4228280000000001 0.25833930910242614
  
