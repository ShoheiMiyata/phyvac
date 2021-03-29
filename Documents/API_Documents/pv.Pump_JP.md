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
対象システム：ポンプ2台、初期値1台、増段のサンプル  
<img src="https://user-images.githubusercontent.com/27459538/112746375-55871480-8fe9-11eb-8b22-dee30ced54fb.png" width=40%>

  
```
import phyvac as pv # 必要なモジュールのインポート
import matplotlib.pyplot as plt
import numpy as np

result = np.zeros((60,3))
CP1 = pv.Pump() # CP1の定義(特性はデフォルト値を利用)
UnitNum_CP1 = pv.UnitNum(thre_up=[0.3], thre_down=[0.2], t_wait=15) # CP1の台数制御の定義

for calstep in range(60):
    branch_g = calstep*0.01 # 流量が毎時刻0.01増加するものとする
    CP1.num = UnitNum_CP1.control(g=branch_g) # 台数制御の実行
    result[calstep,0] = calstep
    result[calstep,1] = CP1.num
    result[calstep,2] = branch_g
    

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(result[:,0], result[:,1], c="r", label="num")
ax.plot(result[:,0], result[:,2], c="b", label="flow")
ax.grid(axis='both')
ax.legend() # 凡例の表示
ax.set_xlabel('calstep') # x軸のラベル
ax.set_ylabel("num,flow") # y軸のラベル
```
> 結果  
> <img src="https://user-images.githubusercontent.com/27459538/112747216-cda40900-8fee-11eb-839b-52a34299483a.png" width=40%>
  
対象システム：ポンプ3台、初期値3台、減段のサンプル  
<img src="https://user-images.githubusercontent.com/27459538/112747245-00e69800-8fef-11eb-86c7-ad7a30870d61.png" width=40%>
  
```
import phyvac as pv # 必要なモジュールのインポート
import matplotlib.pyplot as plt
import numpy as np

result = np.zeros((60,3))
CP1 = pv.Pump() # CP1の定義(特性はデフォルト値を利用)
CP1.num = 3
UnitNum_CP1 = pv.UnitNum(thre_up=[1.2,2.2], thre_down=[1.0,2.0], t_wait=15,num=3) # CP1の台数制御の定義
UnitNum_CP1.num = 3

for calstep in range(60):
    branch_g = 3.0-calstep*0.05 # 流量が3.0から毎時刻0.05減少するものとする
    CP1.num = UnitNum_CP1.control(g=branch_g) # 台数制御の実行
    result[calstep,0] = calstep
    result[calstep,1] = CP1.num
    result[calstep,2] = branch_g
    

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(result[:,0], result[:,1], c="r", label="num")
ax.plot(result[:,0], result[:,2], c="b", label="flow")
ax.grid(axis='both')
ax.legend() # 凡例の表示
ax.set_xlabel('calstep') # x軸のラベル
ax.set_ylabel("num,flow") # y軸のラベル
```
> 結果  
> <img src="https://user-images.githubusercontent.com/27459538/112747511-fa592000-8ff0-11eb-8a52-e67736ed8867.png" width=40%>
