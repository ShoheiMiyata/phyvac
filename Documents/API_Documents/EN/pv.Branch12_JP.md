## pv.Branch100(valve, pump, kr_eq=0.8, kr_pipe=0.5)
Basic branch with pumps , equipment, and bypass valves
  
<img src="https://user-images.githubusercontent.com/27459538/112748089-86b91200-8ff4-11eb-8a36-dcc765ff2361.png" width=30%>

  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|valve|object|Bypass valves' object|
|pump|object|Pump objects on this branch|
|kr_eq|float|Equipment pressure drop \[kPa/(m<sup>3</sup>/min)<sup>2</sup>]|
|kr_pipe|float|Pressure drop in pipe with pump \[kPa/(m<sup>3</sup>/min)<sup>2</sup>]|
|kr_pipe_bypass|float|Pressure drop in bypass piping \[kPa/(m<sup>3</sup>/min)<sup>2</sup>]|
|g|float|流量 \[m<sup>3</sup>/min] |
|dp|float|Branch inlet/outlet pressure difference [kPa] Against flow direction: Pressurization: +, Depressurization: - |
  
## pv.Branch12.f2p(g) To Be Developed!
Calculate the pressure difference from the flow rate

### returns:
Pressure difference between branches（the value of dp is also stored）
## pv.Branch12.p2f(dp)
Calculate flow rate from pressure difference
  
### returns:
Flow rate（the value of g is also stored）
  
## Sample codes
```
import phyvac as pv

CP1 = pv.Pump()
Vlv_Bypass = pv.Valve()

Branch_aPEVb = pv.Branch11(valve=Vlv_Bypass, pump=CP1)
print(Branch_aPEVb.pump.inv, Branch_aPEVb.kr_pipe_pump, Branch_aPEVb.g, Branch_aPEVb.dp)
```
> 0.0 0.5 0.0 0.0
```
CP1.inv = 0.4
Vlv_Bypass.vlv = 0.2
dp1 = Branch_aPEVb.f2p(2.1) # Calculate the inlet/outlet pressure difference of a branch at a flow rate of 2.1 m3/min
print(dp1, Branch_aPEVb.dp, Branch_aPEVb.g, CP1.g, Vlv_Bypass.g)
```
> 15.822870003374664 15.822870003374664 2.1 2.214853606868385 0.11485360686838497
```
Branch_aPEVb.f2p(2.1) # Execution is possible without specifying a return value
print(Branch_aPEVb.dp, Branch_aPEVb.g, CP1.g, Vlv_Bypass.g)
```
> 15.822870003374664 2.1 2.214853606868385 0.11485360686838497
