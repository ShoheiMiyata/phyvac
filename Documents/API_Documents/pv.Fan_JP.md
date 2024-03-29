## pv.Fan(pg=[948.66, -0.5041, -0.097], eg=[0.0773, 0.0142, -1.00e-04], r_ef=0.6)
ファン特性と消費電力の計算  
<img src="https://user-images.githubusercontent.com/27459538/112824603-b2f09380-90c5-11eb-8e10-45acdd9ef187.png" width=40%>
  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|pg|list|圧力-流量(pg)曲線の係数 [切片、一次、二次]|
|eg|list|効率-流量(eg)曲線の係数 [切片、一次、二次]|
|inv|float|インバータ周波数比(min:0.0~max:1.0)|
|dp|float|ファン揚程 [Pa]|
|g|float|流量[m3/min]|
|pw|float|消費電力[kW]|
|ef|float|効率(0.0~1.0)|
|flag|float|計算に問題があったら1、なかったら0|
  
## pv.Fan.f2p(g)
流量gに基づいて揚程を算出する
  
### returns:
揚程dp
  
## pv.Fan.f2p_co()
揚程を表す流量の関数の係数を出力する
  
### returns:
リスト[切片, 1次, 2次]
  
## pv.Pump.cal()
消費電力を算出する
  
### returns:
消費電力pw
  
  
## サンプルコード  
```
import phyvac as pv # 必要なモジュールのインポート

SA1 = pv.Fan() # SA1の定義(特性はデフォルト値を利用)
SA1.inv = 0.8 # invの入力
SA1.f2p(g=1.5) # invが0.8, 流量1.5 m3/min時の揚程を算出
SA1.cal() # 上記条件下での消費電力を算出

print(SA1.g, SA1.dp, SA1.pw)
```
> 結果  
> 1.5 0.4228280000000001 0.25833930910242614
  
