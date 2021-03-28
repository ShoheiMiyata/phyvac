## pv.PID(mode=1, a_max=1, a_min=0, kp=0.8, ti=10, sig=0, t_reset=30, kg=1, t_step=1)
PI制御（D成分は省略されている）
  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|mode|integer|運転モード：運転時1, 非運転時0|
|a|float|ポンプINVや弁開度などの制御値(0~1)|
|a_max,a_min|float|制御値の最大・最小範囲(0~1)|
|kp|float|比例ゲイン|
|ti|float|積分時間|
|sv|float|設定値|
|mv|float|設定値に対する計測値（制御目標値）。流量や温度など。|
|sig|float|sv-mvの積分値|
|t_reset|float|積分リセット(sv-mvの正負がt_resetの間常に同一である場合にsigを0とする)|
|kg|float|aの増減とmvの増減の方向が一致する場合は1、逆の場合は-1|
|t_step|integer|制御ステップ。1だと毎時刻制御出力し、2だと2時刻ごとに制御出力する。|
  
## pv.PID.control(sv, mv)
設定値sv、計測値mvに基づくPI制御値を出力する
  
### returns:
制御値a
  
## サンプルコード
<img src="https://user-images.githubusercontent.com/27459538/112744451-1e116b80-8fdb-11eb-8a7b-259e715efa2c.png" width=30%>

  
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

