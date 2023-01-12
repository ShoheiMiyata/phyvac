## pv.Valve(cv_max=800, r=100)
Characteristics of valves  
<img src="https://user-images.githubusercontent.com/27459538/112825297-8db05500-90c6-11eb-996e-51355f95a5f7.png" width=40%>
  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|cv_max|float|Coefficient of flow rate|
|r|float|Range ability。最も弁を閉じたときの流量比の逆数|
|vlv|float|Valve opening degree(0.0~1.0)|
|dp|float|Pressure loss [kPa]|
|g|float|Flow rate[m3/min]|
  
## pv.Pump.f2p(g)
Calculate pump's lift by g
  
### returns:
Pressure loss dp
  
## pv.Pump.p2f(dp)
Calculate flow rate by dp
  
### returns:
Flow rate g
  
## pv.Pump.f2p_co()
Output the function of flow rate that represents pressure loss
  
### returns:
List[slicing, primary, secondary]
  
## Sample codes  
```
import phyvac as pv
Valve1 = pv.Valve()
Valve1.vlv = 0.6
Valve1.f2p(1.3)
print(Valve1.dp)
```
> Result
> -50.898105429006975
  
```
Valve1.vlv = 0.0 # Valves are totally closed
Valve1.f2p(0.5) # Flow rate = 0.5
print(Valve1.dp)
```
> Result (Output: pressure loss = -99999999 when valves are totally closed (infinity))
> -99999999
