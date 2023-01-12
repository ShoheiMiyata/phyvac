## pv.Pump_para(pump, num=2, valve=None, kr_pipe_pump=0.0, kr_pipe_valve=0.0)
Unit of multiple pumps and bypass valve (can be handled in the same way as Pump, without bypass valve)
  
<img src="https://user-images.githubusercontent.com/27459538/112747938-8409ed00-8ff3-11eb-8d76-121f99063dd5.png" width=30%>

  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|pump|object|Pump object。Only one type of pump can be selected|
|num|int|Number of pumps。More than one。|
|valve|object|Bypass valve object|
|kr_pipe_pump|float|Pressure drop in pipe with pump \[kPa/(m<sup>3</sup>/min)<sup>2</sup>]|
|kr_pipe_valve|float|Pressure drop in pipe with bypass valve \[kPa/(m<sup>3</sup>/min)<sup>2</sup>]|
|dp|float|Branch inlet/outlet pressure difference \[kPa] According to flow direction: Pressurization: +, Depressurization: -|
|g|float|Flow rate \[m<sup>3</sup>/min] |
  
## pv.Pump_para.f2p(g)
Calculate the inlet/outlet pressure difference by flow rate
  
### returns:
Pressure difference at the branch (the value of dp is also included)
## pv.Pump_para.p2f(dp)
Calculate the inlet/outlet flow rate by pressure difference
  
### returns:
Flow rate (the value of g is also included)
  
## Sample codes
```
import phyvac as pv

CP1 = pv.Pump()
Valve1 = pv.Valve()
CP1s = pv.Pump_para(pump=CP1, num=3, valve=Valve1, kr_pipe_pump=0.5, kr_pipe_valve=0.5)

# When flow rate is high
CP1.inv = 0.8
Valve1.vlv = 0.0
print(CP1s.pump.inv,CP1s.num, CP1s.valve.vlv)
print(CP1s.f2p(6.0), CP1s.p2f(136.85))
```
> 0.8 3 0.0  
> 136.85248 6.000436759321203
```
# When flow rate is low
CP1.inv = 0.4
CP1.num = 1
Valve1.vlv = 0.3
print(CP1s.pump.inv,CP1s.valve.vlv)
print(CP1s.f2p(0.5), CP1s.p2f(37.53115))
```
> 0.4 0.3  
> 37.53115207979398 0.5000138162955189
```
# Available in Branch as well as Pump object
CP1.inv = 0.8
CP1s = pv.Pump_para(pump=CP1, num=1, valve=None, kr_pipe_pump=0.0, kr_pipe_valve=0.0)
Branch0 = pv.Branch_w(pump=CP1, kr_pipe=0.0, kr_eq=0.0)
Branch1 = pv.Branch_w(pump=CP1s, kr_pipe=0.0, kr_eq=0.0)
print(Branch0.f2p(2.0),Branch0.p2f(138.85248))
print(Branch1.f2p(2.0),Branch1.p2f(138.85248))
```
> 138.85248 2.000000000000001  
> 138.85248 2.000000000000001

