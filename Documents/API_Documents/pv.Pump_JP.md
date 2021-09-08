## pv.Pump(pg=[233,5.9578,-4.95], eg=[0.0099,0.4174,-0.0508], r_ef=0.8)
### ポンプ単体機器モジュール  
<img src="https://user-images.githubusercontent.com/27459538/112824603-b2f09380-90c5-11eb-8e10-45acdd9ef187.png" width=40%>
  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|pg|list|圧力-流量(pg)曲線の係数 [切片、一次、二次]|
|eg|list|効率-流量(eg)曲線の係数 [切片、一次、二次]|
|inv|float|インバータ周波数比(0.0~1.0)|
|dp|float|ポンプ揚程 [kPa]|
|g|float|流量[m3/min]|
|pw|float|消費電力[kW]|
|r_ef|float|定格効率(0.0~1.0)|
  
## pv.Pump.f2p(g)
gに基づいて揚程を算出する
  
### returns:
揚程dp

## pv.Pump.p2f(dp)
dpに基づいて流量を算出する
  
### returns:
流量g
  
## pv.Pump.f2p_co()
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

CP1 = pv.Pump() # CP1の定義(特性はデフォルト値を利用)
CP1.inv = 0.8 # invの入力
CP1.f2p(g=1.5) # invが0.8, 流量1.5 m3/min時の揚程を算出
CP1.cal() # 上記条件下での消費電力を算出

print(CP1.g, CP1.dp, CP1.pw)
```
> 結果  
> 1.5 145.13186000000002 8.001649808763627
  
