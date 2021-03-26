## pv.Branch10(pump, kr_eq=0.8, kr_pipe=0.5)
ポンプ、機器を有する枝
  
<img src="https://user-images.githubusercontent.com/27459538/112588155-41ed7980-8e42-11eb-8508-249b09dc15c1.png" width=30%>

  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|pump|object|この枝上のポンプのオブジェクト|
|kr_eq|float|機器の圧力損失 \[kPa/(m<sup>3</sup>/min)<sup>2</sup>]|
|kr_pipe|float|管の圧力損失 \[kPa/(m<sup>3</sup>/min)<sup>2</sup>]|
|g|float|流量 \[m<sup>3</sup>/min] |
|dp|float|枝の出入口圧力差 \[kPa] 流れの向きに対して加圧：+, 減圧：- |
  
## pv.Branch10.f2p(g)
流量から圧力差を求める
  
### returns:
枝の圧力差（変数dpにも値は格納される）
## pv.Branch10.p2f(dp)
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
dp1 = Branch_aEb.f2p(2.1) # 流量2.1 m3/minの時の圧力損失を算出
print(dp1, Branch_aEb.dp, Branch_aEb.g)
```
> -7.938000000000001 -7.938000000000001 2.1
```
g1 = Branch_aEb.p2f(-8.0) # 圧力差が-8.0 kPaの時の流量を算出
print(g1, Branch_aEb.g, Branch_aEb.dp)
```
> 2.1081851067789192 2.1081851067789192 -8.0
```
Branch_aEb.f2p(2.1) # 返り値を指定しなくても関数の実行は可能
print(Branch_aEb.dp, Branch_aEb.g)
```
> -7.938000000000001 2.1
