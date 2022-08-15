## **pv.AbsorptionChillerESS(tin_cd=32, tin_ch=15, tout_ch=7, tin_h=37, tout_h=45)**

省エネルギー基準に基づいた吸収式冷温水発生機モデル

能力・燃料消費量・COPの計算

計算できる範囲: 冷却水入口温度(20℃～32℃), 冷水出口温度(5℃～12℃), 温水出口温度(45℃～60℃), 冷房運転時部分負荷(0.2～1.0), 暖房運転時部分負荷(0.1～1.0)

### **Parameters:**

| name             | type  | description                                 |
| ---------------- | ----- | ------------------------------------------- |
| tin_cd           | float | 冷却水入口温度 [℃]                          |
| tin_ch           | float | 冷水入口温度 [℃]                            |
| tout_ch          | float | 冷水出口温度 [℃]                            |
| tin_h            | float | 温水入口温度 [℃]                            |
| tout_h           | float | 温水出口温度 [℃]                            |
| rated_capacity   | float | 定格冷房(暖房)能力 [kW]                     |
| rated_input_fuel | float | 定格冷房(暖房)燃料(都市ガス13A)消費量 [Nm3] |
| g                | float | 冷水流量 [m3/min]                           |
| power_c          | float | 消費電力 [kW]                               |

## **pv.AbsorptionChillerESS.cal_c(rated_capacity, rated_input_fuel, g, power_c)**

冷房の定格値(rated_capacity, rated_input_fuel, power_c)と冷水流量(g)から、運転時の冷凍能力・燃料消費量・COPを算出する

### returns:

冷凍能力(capacity)・燃料消費量(input_fuel)・COP(cop)

## **pv.AbsorptionChillerESS.cal_h(rated_capacity, rated_input_fuel, g, power_c)**

暖房の定格値(**(**rated_capacity, rated_input_fuel, power_c)と温水流量(g)から、運転時の暖房能力・燃料消費量・COPを算出する

### **returns:**

暖房能力(capacity)・燃料消費量(input_fuel)・COP(cop)

## **サンプルコード**

```python
import phyvac as pv   # 必要なモジュールのインポート

ac = pv.AbsorptionChillerESS()   # 機器acの定義、デフォルト温度で計算する
ac.cal_c(rated_capacity=1055, rated_input_fuel=75, g=1.89, power_c=10.4)   # 冷房の計算
print(ac.capacity, ac.input_fuel, ac.cop)
```

> 結果
>
> 1056.110396544 89.99721001979998 1.029981280158948

```python
ac.cal_h(rated_capacity=895, rated_input_fuel=83, g=1.6, power_c=10.4)   # 暖房の計算
print(ac.capacity, ac.input_fuel, ac.cop)
```

> 結果
>
> 884.3633877333333 82.01358791270019 0.9455084558770633
