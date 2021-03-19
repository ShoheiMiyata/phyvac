## pv.Branch00(kr_eq=0.8, kr_pipe=0.5, head_act=0)
機器のみを有する枝
  
<img src="https://user-images.githubusercontent.com/27459538/111766590-0d7d3900-88e9-11eb-91a8-8359b90be87b.png" width=30%>
  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|kr_eq|float|機器の圧力損失 \[kPa/(m<sup>3</sup>/min)<sup>2</sup>]|
|kr_pipe|float|管の圧力損失 \[kPa/(m<sup>3</sup>/min)<sup>2</sup>]|
|heat_act|float|実揚程 \[kPa] (開放系での実揚程)|
|g|float|流量 \[m<sup>3</sup>/min] |
|dp|float|枝の出入口圧力差 \[kPa] 加圧：+, 減圧：- |
  
## pv.Branch00.f2p(g)
流量から圧力差を求める
  
### returns:
dp \[kPa]
## pv.Branch00.p2f(dp)
枝の圧力差（変数dpにも値は格納される）
  
### returns:
流量（変数gにも値は格納される）
  
## サンプルコード
```
import phyvac as pv
```
