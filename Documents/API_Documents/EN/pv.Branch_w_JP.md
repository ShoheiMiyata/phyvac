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
流量から圧力差を求める
  
### returns:
枝の圧力差（変数dpにも値は格納される）
## pv.Branch_w.p2f(dp)
圧力差から流量を求める
  
### returns:
流量（変数gにも値は格納される）
  
## サンプルコード
```
import phyvac as pv

CP1 = pv.Pump()
Branch_aPEb = pv.Branch10(pump = CP1, kr_eq=1.3)
print(Branch_aPEb.pump.inv, Branch_aPEb.kr_pipe, Branch_aPEb.g, Branch_aPEb.dp)
```
> 0.0 0.5 0.0 0.0
```
CP1.inv = 0.8
dp1 = Branch_aPEb.f2p(2.1) # 流量2.1 m3/minの時の枝の出入口圧力差を算出
print(dp1, Branch_aPEb.dp, Branch_aPEb.g)
```
> 129.361604 129.361604 2.1
```
g1 = Branch_aPEb.p2f(120.0) # 枝の出入口圧力差が120.0 kPaの時の流量を算出
print(g1, Branch_aPEb.dp, Branch_aPEb.g)
```
> 2.4598822345001583 120.0 2.4598822345001583
```
Branch_aPEb.f2p(2.1) #　返り値を指定しなくても関数の実行は可能
print(Branch_aPEb.dp, Branch_aPEb.g)
```
> 129.361604 2.1
