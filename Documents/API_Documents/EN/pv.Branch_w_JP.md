## pv.Branch_w(pump=None, valve=None, kr_eq=0.0, kr_pipe=0.0)
Basic branches of water piping   
Basic branch with pumps (parallel pump (with bypass valve) units are acceptable), valves, and equipment in series
  
<img src="https://user-images.githubusercontent.com/27459538/124419774-2545d380-dd99-11eb-88d9-2113fe5dac7d.png" width=30%>

  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|pump|object|Pump's object 。pump_para is also acceptable|
|pump|object|Two-way valve object|
|kr_eq|float|Equipment pressure drop \[kPa/(m<sup>3</sup>/min)<sup>2</sup>]|
|kr_pipe|float|Pipe pressure drop \[kPa/(m<sup>3</sup>/min)<sup>2</sup>]|
|g|float|Flow rate \[m<sup>3</sup>/min] |
|dp|float|Branch inlet/outlet pressure difference \[kPa] Against flow direction: Pressurization: +, Depressurization: - |
  
## pv.Branch_w.f2p(g)
Calculate the pressure difference from the flow rate
  
### returns:
Pressure difference at the branch （the value of dp is also stored）
## pv.Branch_w.p2f(dp)
Calculate flow rate from pressure difference

### returns:
Flow rate（the value of g is also stored）
  
## Sample codes
```
import phyvac as pv

CP1 = pv.Pump()
Branch_aPEb = pv.Branch10(pump = CP1, kr_eq=1.3)
print(Branch_aPEb.pump.inv, Branch_aPEb.kr_pipe, Branch_aPEb.g, Branch_aPEb.dp)
```
> 0.0 0.5 0.0 0.0
```
CP1.inv = 0.8
dp1 = Branch_aPEb.f2p(2.1) # Calculate the inlet/outlet pressure difference of a branch at a flow rate of 2.1 m3/min
print(dp1, Branch_aPEb.dp, Branch_aPEb.g)
```
> 129.361604 129.361604 2.1
```
g1 = Branch_aPEb.p2f(120.0) # Calculate flow rate at a branch inlet/outlet pressure difference of 120.0 kPa
print(g1, Branch_aPEb.dp, Branch_aPEb.g)
```
> 2.4598822345001583 120.0 2.4598822345001583
```
Branch_aPEb.f2p(2.1) #　Function execution is possible without specifying a return value
print(Branch_aPEb.dp, Branch_aPEb.g)
```
> 129.361604 2.1
