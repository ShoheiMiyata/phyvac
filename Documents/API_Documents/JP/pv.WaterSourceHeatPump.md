## pv.WaterSourceHeatPump(filename='-', sheet_name='-')
水熱源ヒートポンプの消費電力・熱源水出口温度を計算  ![スクリーンショット 2023-12-14 135135](https://github.com/ShoheiMiyata/phyvac/assets/140803199/fcff1c46-6bba-43ab-9f09-fdfd4cbe44e8)

 
  
入力ファイル例  
  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|filename|str|機器情報ファイル名（エクセルファイル）|
|sheet_name|str|対象機器情報が記載されたシート名|
|cc_d|float|定格冷房能力 [kW]|
|mode|float|冷房時1,暖房時2で切り替え|
|hc_d|float|定格暖房能力 [kW]|
|tin_ch|float|負荷側入口水温['C]|
|tout_ch|float|負荷側出口水温 ['C]|
|tin_cn|float|熱源側入口水温['C]|
|tout_ch_d|float|冷水出口温度設定値['C]|
|tout_cn|float|熱源側出口水温['C]|
|g_ch|float|負荷側流量[L/min]|
|g_cn|float|熱源側流量[L/min]|
|q|float|熱負荷[kW]|
|pw|float|電力消費量[kW]|
|cop|float|COP[-]|
|flag|int||

  
## pv.WaterSourceHeatPump.cal(mode, q, g_cn, tin_ch, tin_cn)
熱負荷、負荷側入口水温、熱源側流量・入口水温に基づいて各出口温度と消費電力を算出する。

  
### returns:
なし（変数の値が更新される）
  
## サンプルコード  
```
import phyvac as pv

WSHP1 = pv.WaterSourceHeatPump(filename='equipment_spec.xlsx', sheet_name='WaterSourceHeatPump')  # WSHP1の定義
WSHP1.cal(mode=1, q=120, g_cn=200, tin_ch=12.0, tin_cn=20.0)  # 運転条件の入力と計算
print(WSHP1.pw, WSHP1.cop, WSHP1.tout_cn)  # 計算結果例のプリント
```
> phyvac: ver20231116  
> 191.53281318240622 0.7949125596184419 7.2850876575623
  
