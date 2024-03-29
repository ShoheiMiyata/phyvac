## pv.Branch_a(fan=None, damper=None, kr_eq=0.0, kr_duct=0.0)
ファン・ダンパ・機器が並んだダクトの基本的な枝（デフォルトではファン・ダンパ・機器はなし）  
  
<img src="https://user-images.githubusercontent.com/27459538/124419774-2545d380-dd99-11eb-88d9-2113fe5dac7d.png" width=30%>

  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|pump|object|ポンプのオブジェクト。pump_paraも可|
|pump|object|二方弁のオブジェクト|
|kr_eq|float|機器の圧力損失 \[kPa/(m<sup>3</sup>/min)<sup>2</sup>]|
|kr_pipe|float|管の圧力損失 \[kPa/(m<sup>3</sup>/min)<sup>2</sup>]|
|g|float|流量 \[m<sup>3</sup>/min] |
|dp|float|枝の出入口圧力差 \[kPa] 流れの向きに対して加圧：+, 減圧：- |
  
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
