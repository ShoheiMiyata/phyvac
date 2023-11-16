## pv.AirSourceHeatPump(filename='equipment_spec.xlsx', sheet_name='Chiller')
冷凍機の性能曲線に基づく運転点の計算  
  
<img src="https://github.com/ShoheiMiyata/phyvac/assets/27459538/5ad1f231-fa98-4c6c-a09e-64674bdcc7f7" width=60%>  
  
入力ファイル例  
  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|filename|str|機器情報ファイル名（エクセルファイル）|
|sheet_name|str|対象機器情報が記載されたシート名|
|q_ch_d|float|定格能力 [kW]|
|pw_d|float|定格消費電力 [kW]|
|tin_ch_d|float||
|tout_ch_d|float|定格冷水出口温度 ['C]|
|tin_ch|float||
|tout_ch|float||
|tout_ch_sp|float||
|g_ch|float||
|q_ch|float||
|pw|float||
|pl|float||
|cop|float||
|tdb|float|外気乾球温度 ['C]|
|kr_ch|float||
|dp_ch|float||
|flag|int||
  
## pv.AirSourceHeatPump.cal(tout_ch_sp, tin_ch, g_ch, tdb)
冷水出口温度設定、冷水入口温度、冷水流量、外気乾球温度に基づいて出口温度と消費電力を算出する。
また、冷水における圧力損失も算出する
  
### returns:
なし（変数の値が更新される）
  
## サンプルコード  
```
import phyvac as pv

ASHP1 = pv.AirSourceHeatPump(filename='equipment_spec.xlsx', sheet_name='AirSourceHeatPump')  # ASHP1の定義
ASHP1.cal(tout_ch_sp = 7.0, tin_ch = 12.0, g_ch=0.15, tdb=25.0)  # 運転条件の入力と計算
print(ASHP1.pw, ASHP1.pl, ASHP1.tout_ch)  # 計算結果例のプリント
```
> phyvac: ver20231116  
> 5.579090966913902 0.6976744186046512 7.0
  
