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

result = np.zeros((60,2))
CP1 = pv.Pump() # CP1の定義(特性はデフォルト値を利用)
Branch = pv.Branch10(pump=CP1, kr_eq=1.3, kr_pipe=0.8) # ループ(枝)の定義
PID_CP1 = pv.PID(kp=0.1, ti=30, a_min=0.0,t_reset=60) # CP1のPID制御の定義

for calstep in range(60):
    CP1_g_sv = 1.5 # 流量設定値を1.5 m3/minとする
    CP1.inv = PID_CP1.control(sv=CP1_g_sv,mv=CP1.g) # PI制御の実行
    Branch.p2f(dp=0) # Branchの出入口圧力差=0として単一閉ループの流量計算を行う
    result[calstep,0] = calstep
    result[calstep,1] = CP1.g
    
plt.plot(result[:,0], result[:,1]) # 結果の描画
plt.xlabel("calstep") # x軸のラベル
plt.ylabel("flow") # y軸のラベル
plt.show()  
```
> 結果（kp=0.1, ti=30の場合）  
> <img src="https://user-images.githubusercontent.com/27459538/112745087-bf4ef080-8fe0-11eb-93c3-b0092d55cb1f.png" width=40%>
  
> kp=0.02, ti=30とした場合（比例ゲインが小さくなるため、設定値に達するまでに要する時間が長くなる）  
> <img src="https://user-images.githubusercontent.com/27459538/112745137-371d1b00-8fe1-11eb-97cb-c3ce5f81ba8a.png" width=40%>
  
> kp=0.02, ti=3とした場合（積分時間を小さくすると、直前の計測値と設定値とのずれの影響が大きくなるため振動する）
> <img src="https://user-images.githubusercontent.com/27459538/112745258-0093d000-8fe2-11eb-90e9-2da8ccc8d93a.png" width=40%>
  
> kp=0.1, ti=30, t_step=3とした場合（3時間ステップごとに制御が実行される）  
> <img src="https://user-images.githubusercontent.com/27459538/112745407-27063b00-8fe3-11eb-98bd-527d565f8ca8.png" width=40%>
