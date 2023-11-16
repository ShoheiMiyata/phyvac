## pv.Chiller(filename='equipment_spec.xlsx', sheet_name='Chiller')
冷凍機の性能曲線に基づく運転点の計算  
  
<img src="https://github.com/ShoheiMiyata/phyvac/assets/27459538/fbe5eb70-bb6e-4bd2-96f8-1dceb7a4b7d2.png" width=80%>  
  
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
|g_ch_d|float||
|tin_cd_d|float||
|tout_cd_d|float||
|g_cd_d|float||
|tin_ch|float||
|tout_ch|float||
|tout_ch_sp|float||
|g_ch|float||
|tin_cd|float||
|tout_cd|float||
|g_cd|float||
|q_ch|float||
|pw|float||
|pl|float||
|cop|float||
|kr_ch|float||
|kr_cd|float||
|dp_ch|float||
|dp_cd|float||
|flag|int||
  
## pv.Chiller.cal(out_ch_sp, tin_ch, g_ch, tin_cd, g_cd)
冷水出口温度、冷水・冷却水の流量・入口温度に基づいて各出口温度と消費電力を算出する。
また、冷水・冷却水における圧力損失も算出する
  
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
  
