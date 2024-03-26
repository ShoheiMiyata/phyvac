# phyvac

python+hvac => phyvac [fívək | fái-]  

## Tutorial  
[How to create a main code](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/Tutorials/How%20to%20create%20a%20main%20code.md) - [メイン文のつくり方](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/Tutorials/%E3%83%A1%E3%82%A4%E3%83%B3%E6%96%87%E3%81%AE%E3%81%A4%E3%81%8F%E3%82%8A%E6%96%B9.md)  
[Flow balance calculation (water side): 1 AHU, 3 Chillers](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/Tutorials/%E6%B5%81%E9%87%8F%E3%83%90%E3%83%A9%E3%83%B3%E3%82%B9%E8%A8%88%E7%AE%97(%E6%B0%B4%E5%81%B4)%EF%BC%9AAHU1%E5%8F%B0%E3%80%81Chiller3%E5%8F%B0.md)  
[Flow balance calculation (water side): 2 AHUs, 2 Chillers, secondary pump](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/Tutorials/%E6%B5%81%E9%87%8F%E3%83%90%E3%83%A9%E3%83%B3%E3%82%B9%E8%A8%88%E7%AE%97(%E6%B0%B4%E5%81%B4)%EF%BC%9AAHU2%E5%8F%B0%E3%80%81Chiller2%E5%8F%B0%E3%80%81%E9%80%81%E6%B0%B4%E4%BA%8C%E6%AC%A1%E3%83%9D%E3%83%B3%E3%83%97.md)  

## Question and Discussion
Please post anything you care to know!  
https://groups.google.com/g/phyvac


## API Document
[List](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/EN/API_Document_List.md) [リスト](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/API%E3%83%89%E3%82%AD%E3%83%A5%E3%83%A1%E3%83%B3%E3%83%88%E3%83%AA%E3%82%B9%E3%83%88.md)  

## Validation  
The programs are validated based on Guideline of Test Procedure for the Evaluation of Building Energy Simulation Tool (SHASE-G 0023-2022) provided by SHASE (The Society of Heating, Air-Conditioning and Sanitary Engineers in Japan).  
[List](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/Validation/Validation_List_JP.md)  
  
本プログラムは、空気調和・衛生工学会（SHASE）が提供する建物エネルギーシミュレーションツールの評価手法に関するガイドライン（SHASE-G 0023-2022）に基づき検証されています。  
[リスト](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/Validation/Validation_List_JP.md)  

##  Application/Paper 活用事例と関連論文   
[Overview](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/application_overview_EN.pdf)  [概要](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/application_overview_JP.pdf)  
Introduction of phyvac:  
Shohei Miyata, Shanrui Shi, Yasuhori Akashi, Takao Sawachi, Phyvac: a Python module for highly flexible HVAC system simulation, and fault dataset generation as an application example, Proceedings of the 18th IBPSA Conference, pp.915 – 922, https://doi.org/10.26868/25222708.2023.1370  

####  Energy saving quantification/control optimization 省エネ効果・最適制御  
- Energy saving effect on VAV・VWV・CO2 concentration control－VAV・VWV・CO2濃度制御の省エネ効果  
https://doi.org/10.18948/shase.46.293_23  
- Room pressure neutralization 室圧中立化制御：  
https://publications.ibpsa.org/conference/paper/?id=bs2023_1293  

####  Automated fault detection and diagnosis 不具合検知・診断  
- Dataset generation データセット作成：  
https://publications.ibpsa.org/conference/paper/?id=bs2023_1370  
- AFDD using deep learning 深層学習による自動不具合検知・診断：  
https://doi.org/10.18948/shase.47.306_1, https://doi.org/10.1016/j.enbuild.2023.112877  

####  Demand response デマンドレスポンス  
- Behavior of power demand and indoor thermal environment 電力デマンドと室内温熱環境の挙動算出：  
https://doi.org/10.18948/shase.46.286_21  
- Low carbon emission control of chiller using model predictive control モデル予測制御による熱源機器の低炭素制御：  
https://doi.org/10.3130/aije.85.827  

####  Design optimization 最適設計  
- Design method considering operating parameters 運用時の各種パラメータを考慮した設計手法：  
https://doi.org/10.1016/j.jobe.2024.109112

##  Engineering Reference 解説書
Please click [here]() to access.  
[こちら](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/Engineering%20reference_20231129_JP.pdf)より確認できます。

## Update  
- 2023/11    update classes and API document in JP
- 2023/01/18 add validation(AirSourceHeatPump, AbsorptionChiller, CoolingTower)
- 2022/08/31 Pumpモデルで定義時に性能曲線を図示するよう修正
- 2022/08/22 VRFモデル、GeoThermalHPモデル、吸収式冷凍機モデルの追加　その他微修正
- 2021/07/14 湿球温度計算の修正（大気圧の単位修正）、CoolingTowerの比エンタルピー単位修正
- 2021/06/28 Branch00系の廃止、Branch_wの追加（水系Branch）
- 2021/04/02 Branch100の追加（空気系Branch）

## License  
The phyvac is available under a 3-clause BSD-license.

