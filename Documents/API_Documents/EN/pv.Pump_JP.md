## pv.Pump(pg=[233,5.9578,-4.95], eg=[0.0099,0.4174,-0.0508], r_ef=0.8)
### Single pump module 
<img src="https://user-images.githubusercontent.com/27459538/112824603-b2f09380-90c5-11eb-8e10-45acdd9ef187.png" width=40%>
  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|pg|list|Pressure-Flow Rate (pg) coefficient of curve [slicing, primary, secondary]|
|eg|list|Efficiency - Flow Rate (eg) coefficient of curve [slicing, primary, secondary]|
|inv|float|Inverter Frequency Ratio (0.0~1.0)|
|dp|float|Pump's lift [kPa]|
|g|float|Flow Rate[m3/min]|
|pw|float|Electricity Consumption[kW]|
|r_ef|float|Rated efficiency(0.0~1.0)|
 
## pv.Pump.f2p(g)
Calculate the pump's lift by g
  
### returns:
Pump's lift dp

## pv.Pump.p2f(dp)
Calculate the flow rate by dp
  
### returns:
Flow rate g
  
## pv.Pump.f2p_co()
Output the coefficients of the function of the flow rate that represents pump's lift
  
### returns:
List [slicing, primary, secondary]
  
## pv.Pump.cal()
Calculate the electricity consumption
  
### returns:
Electricity consumption pw
  
  
## Sample codes
```
import phyvac as pv # Import needed module

CP1 = pv.Pump() # Definition of CP1 (default values are used for parameters)
CP1.inv = 0.8 # Input inv
CP1.f2p(g=1.5) # Calculate the pump's lift when inv = 0.8 and flow rate = 0.8
CP1.cal() # Calculate the electricity consumption under the conditions above

print(CP1.g, CP1.dp, CP1.pw)
```
> Result 
> 1.5 145.13186000000002 5.978149443740741
  
