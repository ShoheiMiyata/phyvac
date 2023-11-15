### APIドキュメントリスト
### 空調システム  
#### 機器  
- [Chiller]
- [AirSourceHeatPump (空冷ヒートポンプ)]
- [GeoThermalHeatPump_LCEM (地中熱ヒートポンプ LCEMモデル)]
- [AbsorptionChillerESS (吸収式冷温水発生機 省エネ基準モデル)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.AbsorptionChillerESS_JP.md) 
- [Pump (ポンプ)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.Pump_JP.md)
- [Pump_para (並列ポンプ複数台とバイパス弁を有する枝)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.Pump_para_JP.md)
- [Valve (弁)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.Valve_JP.md)
- [HEX_w2w（水-水プレート式熱交換器)]
- [CoolingTower (冷却塔)]
- [CoolingTower_closed (密閉式冷却塔)]
- [AHU (エアハンドリングユニット）]
- [AHU_simple (簡略AHU)]
- [Fan (ファン)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.Fan_JP.md)  
- [Damper (ダンパ)]
- [Coil (コイル)]
- [SprayHumidifier (気化式加湿器)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.SprayHumidifier_JP.md) 
- [SteamSprayHumidifier (蒸気噴霧式加湿器)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.SteamSprayHumidifier_JP.md) 
- [ThermalEnergySystem (蓄熱槽)]
- [BatteryEnergySystem (蓄電池)]
- [VariableRefrigerantFlowEP (ビル用マルチエアコン EnergyPlusモデル)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.VariableRefrigerantFlowEP_JP.md)
- [VariableRefrigerantFlowESS (ビル用マルチエアコン 省エネ基準モデル)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.VariableRefrigerantFlowESS_JP.md)
- [TotalHeatExchanger (全熱交換器)]


#### Branch（配管・ダクト枝）  
- [Branch_w (ポンプ、機器、弁を有する基本的な枝)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.Branch_w_JP.md)
- [Branch100（ポンプ、機器、バイパス弁を有する枝)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.Branch12_JP.md)
#### 制御  
- [PID (PID制御)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.PID_JP.md)
- [UnitNum (台数制御)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.UnitNum_JP.md)

## 室温計算  
#### 読み込み用関数  
- [read_condisions (計算条件の読み込み)]
- [convert_weatherdata (気象データの変換・読み込み)]
#### 要素クラス  
- [Wall (壁)]
- [Window (窓)]
- [Room (室)]
#### 空気状態関数
- [tdb_rh2tdp (乾球温度, 相対湿度→露点温度)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.tdb_rh2tdp_JP.md)
- [tdb_rh2h_x (乾球温度, 相対湿度→比エンタルピー, 絶対湿度)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.tdb_rh2h_x_JP.md)
- [tdb2psat (乾球温度→飽和水蒸気圧)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.tdb2psat_JP.md)
- [tdb_rh2twb (乾球温度, 相対湿度→湿球温度)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.tdb_rh2twb_JP.md)
- [tdb_w2h (乾球温度, 絶対湿度→比エンタルピー)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.tdb_w2h_JP.md)
- [tdb2hsat (乾球温度→飽和水蒸気圧の比エンタルピー)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.tdb2hsat_JP.md)
- [w2pva (絶対湿度→蒸気圧)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.w2pva_JP.md)
- [pva2w (蒸気圧→絶対湿度)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.pva2w_JP.md)
- [h_rh2w (比エンタルピー, 相対湿度→絶対湿度)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.h_rh2w_JP.md)
- [tdb2den (乾球温度→密度)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.tdb2den_JP.md)
- [h_rh2tdb (比エンタルピー, 相対湿度→乾球温度)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.h_rh2tdb_JP.md)
- [tdb_rh2h (乾球温度, 相対湿度→比エンタルピー)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.tdb_rh2h_JP.md)
- [tdb_rh2w (乾球温度, 相対湿度→絶対湿度)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.tdb_rh2w_JP.md)
- [psat2tdp (飽和水蒸気圧→露点温度)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.psat2tdp_JP.md)
- [w_h2tdb (絶対湿度, 比エンタルピー→乾球温度)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.w_h2tdb_JP.md)
- [w_rh2tdb (絶対湿度, 相対湿度→乾球温度)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.w_rh2tdb_JP.md)
- [w2cpair (絶対湿度→水蒸気の定圧比熱)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.w2cpair_JP.md)
- [w_tdb2rh (絶対湿度, 乾球温度→相対湿度)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.w_tdb2rh_JP.md)
- [tdb_twb2w (乾球温度, 湿球湿度→絶対湿度)](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.tdb_twb2w_JP.md)


