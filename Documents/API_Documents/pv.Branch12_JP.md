## pv.Branch12(valve, pump, kr_eq=0.8, kr_pipe=0.5)
ポンプ、機器、バイパス弁を有する枝
  
<img src="https://user-images.githubusercontent.com/27459538/112748089-86b91200-8ff4-11eb-8a36-dcc765ff2361.png" width=30%>

  
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
  
## pv.Branch12.f2p(g) To Be Developed!
流量から圧力差を求める (未実装)
  
### returns:
枝の圧力差（変数dpにも値は格納される）
## pv.Branch12.p2f(dp)
圧力差から流量を求める
  
### returns:
流量（変数gにも値は格納される）
  
## サンプルコード
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
dp1 = Branch_aPEVb.f2p(2.1) # 2.1 m3/min時の枝の出入口温度差
print(dp1, Branch_aPEVb.dp, Branch_aPEVb.g, CP1.g, Vlv_Bypass.g)
```
> 15.822870003374664 15.822870003374664 2.1 2.214853606868385 0.11485360686838497
```
Branch_aPEVb.f2p(2.1) #　返り値を指定しなくても実行は可能
print(Branch_aPEVb.dp, Branch_aPEVb.g, CP1.g, Vlv_Bypass.g)
```
> 15.822870003374664 2.1 2.214853606868385 0.11485360686838497
