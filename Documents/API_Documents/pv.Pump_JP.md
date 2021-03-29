## pv.Pump(pg=[233,5.9578,-4.95], eg=[0.0099,0.4174,-0.0508], r_ef=0.8)
ポンプ特性と消費電力の計算  
<img src="https://user-images.githubusercontent.com/27459538/112745838-43f03d80-8fe6-11eb-8d2b-7ba1e58a3cae.png" width=40%>
  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|pg|list|圧力-流量(pg)曲線の係数 [切片、一次、二次]|
|eg|list|効率-流量(eg)曲線の係数 [切片、一次、二次]|
|inv|float|インバータ周波数比(0.0~1.0)|
|dp|float|ポンプ揚程 [kPa]|
|g|float|流量[m3/min]|
|pw|float|消費電力[kW]|
|ef|float|効率(0.0~1.0)|
|num|integer|（並列時の）運転台数。デフォルトは1|
  
## pv.Pump.f2p(g)
gに基づいて揚程を算出する
  
### returns:
揚程dp
  
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
CP1.inv = 0.8
CP1.f2p(g=1.5)
CP1.cal()

print(CP1.g, CP1.dp, CP1.pw)
```
> 結果  
> 1.5 145.13186000000002 8.001649808763627
  
