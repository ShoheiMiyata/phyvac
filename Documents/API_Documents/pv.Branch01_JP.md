## pv.Branch01(valve, kr_eq=0.8, kr_pipe=0.5)
機器、弁を有する枝
  
<img src="https://user-images.githubusercontent.com/27459538/111778441-00b41180-88f8-11eb-8c16-95e53ee139c6.png" width=30%>

  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|valve|object|この枝上の弁のオブジェクト|
|kr_eq|float|機器の圧力損失 \[kPa/(m<sup>3</sup>/min)<sup>2</sup>]|
|kr_pipe|float|管の圧力損失 \[kPa/(m<sup>3</sup>/min)<sup>2</sup>]|
|g|float|流量 \[m<sup>3</sup>/min] |
|dp|float|枝の出入口圧力差 \[kPa] 流れの向きに対して加圧：+, 減圧：- |
  
## pv.Branch01.f2p(g)
流量から圧力差を求める
  
### returns:
枝の圧力差（変数dpにも値は格納される）
## pv.Branch01.p2f(dp)
圧力差から流量を求める
  
### returns:
流量（変数gにも値は格納される）
  
## サンプルコード
```
import phyvac as pv

Vlv1 = pv.Valve()
Branch_aEVb = pv.Branch01(valve = Vlv1, kr_eq=1.3)
print(Branch_aEVb.valve.vlv, Branch_aEVb.kr_pipe, Branch_aEVb.g, Branch_aEVb.dp)
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
