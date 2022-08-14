## pv.VariableRefrigerantFlowESS()

省エネルギー基準に基づいたビルマルモデル

能力・消費電力・COPの計算

計算できる範囲: 外気乾球温度(冷房, 15~43℃), 外気湿球温度(暖房, -20~15℃), 運転時部分負荷率(0.3~1)

### Parameters:

| name                  | type  | description                     |
| --------------------- | ----- | ------------------------------- |
| rated_capacity        | float | 定格冷房(暖房)能力 [kW]         |
| rated_input_power     | float | 定格冷房(暖房)消費電力 [kW]     |
| rated_indoor_capacity | float | 室内機の冷房(暖房)定格能力 [kW] |
| odb                   | float | 外気乾球温度 [℃]                |
| owb                   | float | 外気湿球温度 [℃]                |

## pv.VariableRefrigerantFlowESS.cal_c(rated_capacity, rated_input_power, rated_indoor_capacity, odb)

冷房の定格値(rated_capacity, rated_input_power, indoor_capacity)と外気乾球温度(odb)から、運転時の冷凍能力・電力消費量・COPを算出する

### returns:

冷凍能力(capacity)・電力消費量(input_power)・COP(cop)

## pv.VariableRefrigerantFlowESS.cal_h(rated_capacity, rated_input_power, rated_indoor_capacity, owb)

暖房の定格値(rated_capacity, rated_input_power, indoor_capacity)と外気湿球温度(owb)により、運転時の暖房能力・電力消費量・COPを算出する

### returns:

暖房能力(capacity)・電力消費量(input_power)・COP(cop)

## **サンプルコード**

```python
import phyvac as pv   # 必要なモジュールのインポート

vrf = pv.VariableRefrigerantFlowESS()   # 機器vrfの定義
vrf.cal_c(rated_capacity=32, rated_input_power=9.7, rated_indoor_capacity=32, odb=35)   # 冷房の計算
print(vrf.capacity, vrf.input_power, vrf.cop)
```

> 結果
>
> 30.399999999999995 11.639999999999999 2.611683848797251

```python
vrf.cal_h(rated_capacity=37.5, rated_input_power=10.6, rated_indoor_capacity=37.5, owb=6)   # 暖房の計算
print(vrf.capacity, vrf.input_power, vrf.cop)
```

> 結果
>
> 35.625 12.719999999999999 2.8007075471698117