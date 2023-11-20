## pv.WaterSourceHeatPump(filename='-', sheet_name='-')
水熱源ヒートポンプの消費電力・熱源水出口温度を計算  
  
<img src="https://github.com/ShoheiMiyata/phyvac/assets/27459538/fbe5eb70-bb6e-4bd2-96f8-1dceb7a4b7d2.png" width=80%>  
  
入力ファイル例  
  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|filename|str|機器情報ファイル名（エクセルファイル）|
|sheet_name|str|対象機器情報が記載されたシート名|
|cc_d|float|定格冷房能力 [kW]|
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

  
## pv.WaterSourceHeatPump.cal(q, g_cn, tin_ch, tin_cn)
熱負荷、負荷側入口水温、熱源側流量・入口水温に基づいて各出口温度と消費電力を算出する。

  
### returns:
なし（変数の値が更新される）
  
## サンプルコード  
```
import phyvac as pv

Chiller1 = pv.Chiller(filename='equipment_spec.xlsx', sheet_name='Chiller')  # Chiller1の定義
Chiller1.cal(tout_ch_sp=7.0, tin_ch=15.0, g_ch=2.5, tin_cd=28.0, g_cd=5.5)  # 運転条件の入力と計算
print(Chiller1.pw, Chiller1.pl, Chiller1.cop)  # 計算結果例のプリント
```
> phyvac: ver20231116  
> 191.53281318240622 0.7949125596184419 7.2850876575623
  
