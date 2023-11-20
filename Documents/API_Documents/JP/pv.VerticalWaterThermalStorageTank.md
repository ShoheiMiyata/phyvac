## pv.VerticalWaterThermalStorageTank(timedelta, depth=6.0, base_area=10.0)
成層型水蓄熱槽モデル  
  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|depth|float|水槽深さ [m]|
|base_area|float|水槽底面積 [m2]|
|timedelta|int|計算時間間隔 [s]|
|tin|float|流入温度 ['C]|
|tout|float|流出温度 ['C]|
|g_w|float|流量[m3/min]|
|t_ambient|float|周囲温度 ['C]|
|sig_downflow|int|流れが下向き：1, 上向き|
|tes_temp|array|温度分布 ['C]|
|t_ref|float|基準温度 ['C]|
|heat|float|蓄熱量 [MJ]|
  
## pv.VerticalWaterThermalStorageTank.cal(tin, g_w, sig_downflow=0, t_ref=15, t_ambient=25)
入口温度tin流量gに基づいて揚程を算出する
  
### returns:
流出温度tout
  
  
## サンプルコード  
```
import phyvac as pv # 必要なモジュールのインポート

TST1 = pv.VerticalWaterThermalStorageTank(timedelta=60, depth=6.0, base_area=10.0)  # 計算時間間隔1分, 容量60m3
for i in range(30):
    tout = TST1.cal(tin=7.0, g_w=2.0, sig_downflow=0, t_ref=15, t_ambient=25)  # 7度2.0m3/minで蓄熱
print(tout, TST1.heat)  # 30分後の流出温度[℃]と蓄熱量[MJ]
for i in range(10):
    tout = TST1.cal(tin=7.0, g_w=2.0, sig_downflow=0, t_ref=15, t_ambient=25)
print(tout, TST1.heat)  # さらに10分後分後の流出温度[℃]と蓄熱量[MJ]
```
> 結果  
> 10.645439966875834 -631.1993750481067  
> 7.496886846549429 -677.5501743807945
