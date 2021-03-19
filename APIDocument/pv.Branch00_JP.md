## pv.Branch00(kr_eq=0.8, kr_pipe=0.5, head_act=0)
機器のみを有する枝
  
<img src="https://user-images.githubusercontent.com/27459538/111773622-be87d180-88f1-11eb-928c-eae0ba653c3a.png" width=30%>
  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|kr_eq|float|機器の圧力損失 \[kPa/(m<sup>3</sup>/min)<sup>2</sup>]|
|kr_pipe|float|管の圧力損失 \[kPa/(m<sup>3</sup>/min)<sup>2</sup>]|
|heat_act|float|実揚程 \[kPa] 開放系での実揚程|
|g|float|流量 \[m<sup>3</sup>/min] |
|dp|float|枝の出入口圧力差 \[kPa] 流れの向きに対して加圧：+, 減圧：- |
  
## pv.Branch00.f2p(g)
流量から圧力差を求める
  
### returns:
枝の圧力差（変数dpにも値は格納される）
## pv.Branch00.p2f(dp)
圧力差から流量を求める
  
### returns:
流量（変数gにも値は格納される）
  
## サンプルコード
```
import phyvac as pv
```
