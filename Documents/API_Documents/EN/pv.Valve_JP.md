## pv.Valve(cv_max=800, r=100)
Characteristics of valves  
<img src="https://user-images.githubusercontent.com/27459538/112825297-8db05500-90c6-11eb-996e-51355f95a5f7.png" width=40%>
  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|cv_max|float|Coefficient of flow rate|
|r|float|Range ability。最も弁を閉じたときの流量比の逆数|
|vlv|float|Valve opening degree(0.0~1.0)|
|dp|float|圧力損失 [kPa]|
|g|float|流量[m3/min]|
  
## pv.Pump.f2p(g)
gに基づいて揚程を算出する
  
### returns:
圧力損失dp
  
## pv.Pump.p2f(dp)
dpに基づいて流量を算出する
  
### returns:
流量g
  
## pv.Pump.f2p_co()
圧力損失を表す流量の関数の係数を出力する
  
### returns:
リスト[切片, 1次, 2次]
  
## サンプルコード  
```
import phyvac as pv # 必要なモジュールのインポート
Valve1 = pv.Valve()
Valve1.vlv = 0.6
Valve1.f2p(1.3)
print(Valve1.dp)
```
> 結果  
> -50.898105429006975
  
```
Valve1.vlv = 0.0 # 全閉時
Valve1.f2p(0.5) # 仮に流量0.5を与える
print(Valve1.dp)
```
> 結果(全閉時は常に圧力損失-99999999 kPaを出力する(無限大を模擬))  
> -99999999
