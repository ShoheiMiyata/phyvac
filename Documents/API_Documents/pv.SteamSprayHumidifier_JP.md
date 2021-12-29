## pv.SteamSprayHumidifier(spec_table=pd.read_excel('EquipmentSpecTable.xlsx', sheet_name='SteamSprayHumidifier', header=None)
蒸気噴霧式加湿器の出口状態の計算

### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|area|float|加湿器面積[m2]|
|dp|float|圧力損失[Pa]|
|sat_eff|float|飽和効率[-]|
|an|float|風速[m/s] - 圧力損失[Pa]のn次の係数|
|tdb_air_in|float|入口空気乾球温度['C]|
|w_air_in|float|入口空気絶対湿度[kg/kg']|
|flowrate_air_in|float|入口空気質量流量[kg/s]|
|t_steam_in|float|入口蒸気温度['C]|
|flowrate_steam_in|float|入口水蒸気流量[kg/s]|
|tdb_air_out|float|出口空気乾球温度['C]|
|w_air_out|float|出口空気絶対湿度[kg/kg']|
|flowrate_air_out|float|出口空気質量流量[kg/s]|
  
## pv.SteamSprayHumidifier.cal(tdb_air_in, w_air_in, flowrate_air_in, flowrate_steam_in, t_steam_in)
入口乾球温度tdb_air_in、入口絶対湿度w_air_in、空気質量流量flowrate_air_in、入口蒸気質量流量flowrate_steam_in、入口蒸気温度t_steam_inを入力値として出口状態と圧力損失dpを算出する
  
### returns:
出口空気温度tdb_air_out、出口絶対湿度w_air_out、加湿量flowrate_water_add、圧力損失dp

  
## サンプルコード  
```
import phyvac as pv # 必要なモジュールのインポート
import pandas as pd

HUM = SprayHumidifier() # HUMの定義(特性はspec_table=pd.read_excel('EquipmentSpecTable.xlsx', sheet_name='SteamSprayHumidifier'を読み込み） 
# 読み込んだ入力特性は以下
# HUM.area = 0.42
# HUM.dp = 45
# HUM.sat_eff = 0.6

# 入口乾球温度=16[℃], 入口空気絶対湿度=0.007[kg/kg’], 空気質量流量= 1.68[kg/s], 加湿蒸気流量=0.0305[kg/s], 加湿蒸気温度=40[℃]のときの出口状態を計算
HUM = SteamSprayHumidifier()
HUM.cal(16, 0.007, 1.68, 0.0305, 40)
print(HUM.tdb_air_out, HUM.w_air_out, HUM.flowrate_air_out, HUM.dp)

```
> 結果  
> 16.776373404224994, 0.007178393753416995, 1.6802976181784912, 45.0
