## pv.CoolingTower(tin_w_d=37.0, tout_w_d=32.0, twb_d=27.0, g_w_d=0.26, g_a_d=123.0, pw_d=2.4, actual_head=2.0, kr=1.0)
冷却塔モデル
  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|tin_w_d|float|定格冷却水入口温度 ['C]|
|tout_w_d|float|定格冷却水出口温度 ['C]|
|twb_d|float|定格湿球温度 ['C]|
|g_w_d|float|定格冷却水流量 [m3/min]|
|g_a_d|float|定格風量 [m3/min]|
|pw_d|float|定格消費電力[kW]|
|actual_head|float|実揚程 [m]|
|kr|float|圧力損失係数 [kPa/(m3/min)2]|
|tin_w|float|冷却水入口温度 ['C]|
|tout_w|float|冷却水出口温度 ['C]|
|g_w|float|冷却水流量 [m3/min]|
|inv|float|ファンインバーター周波数比 [-] (0.0~1.0)|
|pw|float|ファン消費電力 [kW]|
|tdb|float|乾球温度 ['C]|
|rh|float|相対湿度[%] (0.0~100.0)|
  
## pv.CoolingTower.cal(g_w, tin_w, tdb, rh)
冷却水流量g_w, 冷却水入口温度, 外気乾球温度・外気相対湿度に基づいて冷却水出口温度を算出する。
ファン周波数比は事前の入力が必要。
  
### returns:
冷却水出口温度tout_w
  
## サンプルコード  
```
import phyvac as pv # 必要なモジュールのインポート

CT1 = pv.CoolingTower()
CT1.inv = 1.0
print(CT1.inv)
CT1.cal(g_w=0.2, tin_w=37.0, tdb=33.0, rh=50.0)
print(CT1.tout_w)
```
> 結果  
> 1.0  
> 29.784495260341608  
  
