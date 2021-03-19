## pv.Branch00(kr_eq=0.8, kr_pipe=0.5, head_act=0)
A branch with only equipment
  
<img src="https://user-images.githubusercontent.com/27459538/111773622-be87d180-88f1-11eb-928c-eae0ba653c3a.png" width=30%>
  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|kr_eq|float|coefficient of equipment pressure loss \[kPa/(m<sup>3</sup>/min)<sup>2</sup>]|
|kr_pipe|float|coefficient of pipe pressure loss \[kPa/(m<sup>3</sup>/min)<sup>2</sup>]|
|heat_act|float|actual head \[kPa]|
|g|float|flow rate \[m<sup>3</sup>/min] |
|dp|float|differential pressure of the branch \[kPa] Pressurize along the direction of the flow：+, otherwise：- |
  
## pv.Branch00.f2p(g)
calculate differential pressure from flow rate
  
### returns:
differential pressure of the branch (The value is also stored in the variable dp.)
## pv.Branch00.p2f(dp)
calculate flow rate from differential pressure
  
### returns:
flow rate of the branch (The value is also stored in the variable g.)
  
## Sample Code
```
import phyvac as pv # import phyvac module

Branch_aEb = pv.Branch00(kr_eq=1.3) # define a branch from point a through Equipment to point b
print(Branch_aEb.kr_eq, Branch_aEb.kr_pipe, Branch_aEb.g, Branch_aEb.dp)
```
> 1.3 0.5 0.0 0.0
```
dp1 = Branch_aEb.f2p(2.1) # Calculate the pressure loss at a flow rate of 2.1 m3/min
print(dp1, Branch_aEb.dp, Branch_aEb.g)
```
> -7.938000000000001 -7.938000000000001 2.1
```
g1 = Branch_aEb.p2f(-8.0) # Calculate the flow rate when the pressure difference is -8.0 kPa
print(g1, Branch_aEb.g, Branch_aEb.dp)
```
> 2.1081851067789192 2.1081851067789192 -8.0
```
Branch_aEb.f2p(2.1) # The function can be executed without specifying the return value.
print(Branch_aEb.dp, Branch_aEb.g)
```
> -7.938000000000001 2.1
