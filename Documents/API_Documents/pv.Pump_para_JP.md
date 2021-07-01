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

# 流量が大きい場合
CP1.inv = 0.8
Valve1.vlv = 0.0
print(CP1s.pump.inv,CP1s.num, CP1s.valve.vlv)
print(CP1s.f2p(6.0), CP1s.p2f(136.85))
```
> 0.8 3 0.0  
> 136.85248 6.000436759321203
```
# 流量が小さい場合
CP1.inv = 0.4
CP1.num = 1
Valve1.vlv = 0.3
print(CP1s.pump.inv,CP1s.valve.vlv)
print(CP1s.f2p(0.5), CP1s.p2f(37.53115))
```
> 0.4 0.3  
> 37.53115207979398 0.5000138162955189
```
# BranchではPumpオブジェクトと同様に利用可能
CP1.inv = 0.8
CP1s = pv.Pump_para(pump=CP1, num=1, valve=None, kr_pipe_pump=0.0, kr_pipe_valve=0.0)
Branch0 = pv.Branch000(pump=CP1, kr_pipe=0.0, kr_eq=0.0)
Branch1 = pv.Branch000(pump=CP1s, kr_pipe=0.0, kr_eq=0.0)
print(Branch0.f2p(2.0),Branch0.p2f(138.85248))
print(Branch1.f2p(2.0),Branch1.p2f(138.85248))
```
> 138.85248 2.000000000000001  
> 138.85248 2.000000000000001

