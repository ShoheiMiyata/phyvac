## pv.UnitNum(thre_up=[0.5,1.0], thre_down=[0.4,0.9], t_wait=15)
台数制御  
<img src="https://user-images.githubusercontent.com/27459538/112745838-43f03d80-8fe6-11eb-8d2b-7ba1e58a3cae.png" width=40%>
  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|thre_up|list|増段閾値(1台->2台, 2台->3台といった増段閾値) thre: threshold|
|thre_down|list|減段閾値(2台->1台, 3台->2台といった減段閾値) thre: threshold|
|t_wait|integer|効果待ち時間(増減段閾値をt_wait時間連続で上回る・下回った場合に増減段する)|
|num|integer|運転台数|
  
## pv.UnitNum.control(g)
gに基づいて台数制御する
  
### returns:
台数num
  
## サンプルコード
システム図  
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
  
システム図  
<img src="https://user-images.githubusercontent.com/27459538/112747245-00e69800-8fef-11eb-86c7-ad7a30870d61.png" width=40%>
  
```


> kp=0.02, ti=30とした場合（比例ゲインが小さくなるため、設定値に達するまでに要する時間が長くなる）  
> <img src="https://user-images.githubusercontent.com/27459538/112745137-371d1b00-8fe1-11eb-97cb-c3ce5f81ba8a.png" width=40%>
  
> kp=0.02, ti=3とした場合（積分時間を小さくすると、直前の計測値と設定値とのずれの影響が大きくなるため振動する）
> <img src="https://user-images.githubusercontent.com/27459538/112745258-0093d000-8fe2-11eb-90e9-2da8ccc8d93a.png" width=40%>
  
> kp=0.1, ti=30, t_step=3とした場合（3時間ステップごとに制御が実行される）  
> <img src="https://user-images.githubusercontent.com/27459538/112745407-27063b00-8fe3-11eb-98bd-527d565f8ca8.png" width=40%>
