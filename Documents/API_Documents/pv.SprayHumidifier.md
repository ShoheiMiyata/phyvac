## pv.SprayHumidifier()
気化式加湿器の出口状態の計算

<img src="https://user-images.githubusercontent.com/78840483/147629436-70da761d-3b0e-4b91-8e81-bd44aa0aec5f.png" width=40%>
<img src="https://user-images.githubusercontent.com/78840483/147629938-d30c39e5-74e1-4b77-87dc-d0d1ba632cc6.png" width=40%>

### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|d|float|加湿エレメント厚さ[m]|
|area|float|加湿器面積[m2]|
|an|float|風速[m/s] - 圧力損失[Pa]のn次の係数|
|tdb_air_in|float|入口空気乾球温度['C]|
|w_air_in|float|入口空気絶対湿度[kg/kg']|
|flowrate_air_in|float|入口空気質量流量[kg/s]|
|flowrate_water_req|float|要求加湿質量流量[kg/s]|
|tdb_air_out|float|出口空気乾球温度['C]|
|twb_air_out|float|出口空気湿球温度['C]|
|w_air_out|float|出口空気絶対湿度[kg/kg']|
|flowrate_air_out|float|出口空気質量流量[kg/s]|
|flowrate_water_add|float|加湿質量流量[kg/s]|
|dp|float|圧力損失[Pa]|

  
## pv.SprayHumidifier.cal(tdb_air_in, w_air_in, flowrate_air_in, flowrate_water_req)
入口乾球温度、入口絶対湿度、空気質量流量、要求加湿量を入力値として出口空気乾球温度、出口空気湿球温度、出口絶対湿度、加湿量および圧力損失を算出する
  
### returns:
tdb_air_out, twb_air_out, w_air_out, flowrate_water_add, dp

  
## サンプルコード  
```
import phyvac as pv # 必要なモジュールのインポート
import math
import pandas as pd

HUM = SprayHumidifier() # SA1の定義(特性はspec_table=pd.read_excel('EquipmentSpecTable.xlsx', sheet_name='SprayHumidifier'を読み込み）
# 入力機器特性は以下
# HUM.d = 0.075
# HUM.area = 0.675
# HUM.rh_border = 95
# HUM.a2 = 4.2143
# HUM.a1 = -2.1643
# HUM.a0 = 2.1286

# 入口乾球温度=16[℃], 入口空気絶対湿度=0.007[kg/kg’], 空気質量流量= 1.67[kg/s], 要求加湿流量=0.001[kg/s]のときの出口状態を計算
HUM.cal(16, 0.007, 4675 * 1.293 / 3600, 0.001))
print(HUM.tdb_air_out, HUM.twb_air_out, HUM.w_air_out, HUM.flowrate_water_add, HUM.dp)

```
> 結果  
> 14.522529672178925, 13.96484375, 0.007595555665843642, 0.0006339037632936271, 13.56303095776389
