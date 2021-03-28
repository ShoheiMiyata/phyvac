## pv.PID(mode=1, a_max=1, a_min=0, kp=0.8, ti=10, t_reset=30, kg=1, sig=0, t_step=1)
PI制御（D成分は省略されている）
  
<img src="https://user-images.githubusercontent.com/27459538/111773622-be87d180-88f1-11eb-928c-eae0ba653c3a.png" width=30%>
  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|mode|integer|運転モード：運転時1, 非運転時0|
|a_max,a_min|float|制御値の最大・最小範囲(0~1)|
|kp|float|比例ゲイン|
|ti|float|積分時間|
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
import phyvac as pv # phyvacモジュールのインポート

Branch_aEb = pv.Branch00(kr_eq=1.3) # 点aからEquipmentを通って点bまでの枝を定義
print(Branch_aEb.kr_eq, Branch_aEb.kr_pipe, Branch_aEb.g, Branch_aEb.dp)
```
> 1.3 0.5 0.0 0.0
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
