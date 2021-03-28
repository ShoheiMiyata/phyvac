## pv.PID(mode=1, a_max=1, a_min=0, kp=0.8, ti=10, sig=0, t_reset=30, kg=1, t_step=1)
PI制御（本モジュールにおいてD成分は省略されている）
  
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
システム図  
<img src="https://user-images.githubusercontent.com/27459538/112744451-1e116b80-8fdb-11eb-8a7b-259e715efa2c.png" width=40%>

  
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
> 結果  
> <img src="https://user-images.githubusercontent.com/27459538/112745087-bf4ef080-8fe0-11eb-93c3-b0092d55cb1f.png" width=40%>
  
> kp=0.02, ti=30とした場合（比例ゲインが小さくなるため、設定値に達するまでに要する時間が長くなる）  
> <img src="https://user-images.githubusercontent.com/27459538/112745137-371d1b00-8fe1-11eb-97cb-c3ce5f81ba8a.png" width=40%>
  
> kp=0.02, ti=3とした場合（積分時間を小さくすると、直前の計測値と設定値とのずれの影響が大きくなるため振動する）
> <img src="https://user-images.githubusercontent.com/27459538/112745258-0093d000-8fe2-11eb-90e9-2da8ccc8d93a.png" width=40%>
  
> kp=0.3, ti=30, t_step=3とした場合。3時間ステップごとに制御を実行する。
> <img src="https://user-images.githubusercontent.com/27459538/112745407-27063b00-8fe3-11eb-98bd-527d565f8ca8.png" width=40%>
