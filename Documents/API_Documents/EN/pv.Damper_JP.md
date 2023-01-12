## pv.Damper(coef=[[1.0, -0.00001944, 0.018, 0.18, -0.007], [0.8, 0.0000864, 0.036, 0.132, 0.0684],[0.6, 0.001296, 0.072, 0.384, 0.1001], [0.4, 0.00108, 0.36, -0.582, 0.0662],[0.2, -0.0216, 4.32, -5.34, 0.2527]])
ダンパ特性と圧力損失計算  
<img src="https://user-images.githubusercontent.com/78840483/112942379-fb15c180-916a-11eb-9a60-bea897372748.png" width=40%>
<img src="https://user-images.githubusercontent.com/78840483/112946860-fb18c000-9170-11eb-8b8f-59299ecc4ccd.png" width=20%>

  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|damp|float|ダンパ開度[0.0~1.0]|
|dp|float|圧力損失[kPa]|
|g|float|流量[m3/min]|
|coef|list|f2p(dp=a×g2)の圧損係数aのリスト（ダンパ開度は降順）[damp_1,a_damp1]..[dampn,a_damp n]|

  
## pv.Damper.f2p(damp,g)
dampとgに基づいて圧力損失dp(+の値)を算出する
  
### returns:
圧力損失dp
  
## pv.Damper.p2f(damp,dp)
dampとdpに基づいて流量gを算出する
  
### returns:
流量g
  
  
## サンプルコード  
```
import phyvac as pv # 必要なモジュールのインポート

DAMP1 = Damper() # DAMP1の定義(ダンパ特性はデフォルト値を利用)
DAMP1.f2p(damp=0.4, g=10)  # ダンパ開度が0.8, 流量1.5 m3/min時の揚程を算出
print(DAMP1.dp)
DAMP1.p2f(damp=0.4, dp=0.05)
print(DAMP1.g)
```
> 結果  
> 0.0508875127863876
> 9.912413030076587
  
