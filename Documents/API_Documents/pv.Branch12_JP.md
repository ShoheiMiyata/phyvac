## pv.Branch12(valve, pump, kr_eq=0.8, kr_pipe=0.5)
ポンプ、機器、バイパス弁を有する枝
  
<img src="https://user-images.githubusercontent.com/27459538/112600540-afa2a100-8e54-11eb-875d-6598bfbb7713.png" width=30%>

  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|valve|object|バイパス弁のオブジェクト|
|pump|object|この枝上のポンプのオブジェクト|
|kr_eq|float|機器の圧力損失 \[kPa/(m<sup>3</sup>/min)<sup>2</sup>]|
|kr_pipe|float|ポンプのある菅の圧力損失 \[kPa/(m<sup>3</sup>/min)<sup>2</sup>]|
|kr_pipe_bypass|float|バイパス配管の圧力損失 \[kPa/(m<sup>3</sup>/min)<sup>2</sup>]|
|g|float|流量 \[m<sup>3</sup>/min] |
|dp|float|枝の出入口圧力差 \[kPa] 流れの向きに対して加圧：+, 減圧：- |
  
※ポンプの台数はポンプオブジェクトの変数pump.numで指定する
## pv.Branch12.f2p(g) To Be Developed!
流量から圧力差を求める
  
### returns:
枝の圧力差（変数dpにも値は格納される）
## pv.Branch12.p2f(dp) To Be Developed!
圧力差から流量を求める
  
### returns:
流量（変数gにも値は格納される）
  
## サンプルコード
```
import phyvac as pv

CP1 = pv.Pump()
Vlv_CP1 = pv.Valve()
CP1.num = 2 # ポンプ運転台数の指定

Branch_aPVb = pv.Branch11(valve=Vlv_CP1, pump=CP1)
print(Branch_aPVb.pump.inv, Branch_aPVb.kr_pipe_pump, Branch_aPVb.g, Branch_aPVb.dp)
```
> 0.0 0.5 0.0 0.0
```
CP1.inv = 0.3
Vlv_CP1.vlv = 0.4
dp1 = Branch_aPVb.f2p(2.1)
print(dp1, Branch_aPVb.dp, Branch_aPVb.g, CP1.g, Vlv_CP1.g)
```
> 15.357309082033566 15.357309082033566 2.1 1.191954610229136 0.28390922045827205
```
Branch_aPVb.f2p(2.1) #　返り値を指定しなくても実行は可能
print(dp1, Branch_aPVb.dp, Branch_aPVb.g, CP1.g, Vlv_CP1.g)
```
> 15.357309082033566 15.357309082033566 2.1 1.191954610229136 0.28390922045827205
