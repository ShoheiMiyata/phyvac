## pv.Pump_para(pump, num=2, valve=None, kr_pipe_pump=0.0, kr_pipe_valve=0.0)
並列ポンプ複数台とバイパス弁のユニット（Pumpと同様に取扱可能、バイパス弁はなくてもよい）
  
<img src="https://user-images.githubusercontent.com/27459538/112747938-8409ed00-8ff3-11eb-8d76-121f99063dd5.png" width=30%>

  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|pump|object|ポンプオブジェクト。ポンプは1種類のみ指定可能|
|num|int|ポンプ台数。1台以上。|
|valve|object|バイパス弁のオブジェクト|
|kr_pipe_pump|float|ポンプのある菅の圧力損失 \[kPa/(m<sup>3</sup>/min)<sup>2</sup>]|
|kr_pipe_valve|float|バイパス弁の管の圧力損失 \[kPa/(m<sup>3</sup>/min)<sup>2</sup>]|
|dp|float|枝の出入口圧力差 \[kPa] 流れの向きに対して加圧：+, 減圧：- |
|g|float|流量 \[m<sup>3</sup>/min] |
  
## pv.Pump_para.f2p(g)
流量からユニットの出入口圧力差を求める
  
### returns:
枝の圧力差（変数dpにも値は格納される）
## pv.Pump_para.p2f(dp)
圧力差からユニットの出入口流量を求める
  
### returns:
流量（変数gにも値は格納される）
  
## サンプルコード
```
import phyvac as pv

CP1 = pv.Pump()
Valve1 = pv.Valve()
CP1s = pv.Pump_para(pump=CP1, num=3, valve=Valve1, kr_pipe_pump=0.5, kr_pipe_valve=0.5)
CP1.inv=0.4
Valve1.vlv = 0.3
print(CP1s.pump.inv,CP1s.valve.vlv)
```
> 0.4 0.3
```
print(CP1s.f2p(2.0), CP1s.p2f(36.1))
```
> 36.1255047938035 2.014131371912282
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
