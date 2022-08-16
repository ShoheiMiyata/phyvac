## pv.VariableRefrigerantFlowESS(rated_capacity_c, rated_input_power_c, rated_capacity_h, rated_input_power_h)

省エネルギー基準に基づいたビルマルモデル

能力・消費電力・COPの計算

計算できる範囲: 外気乾球温度(冷房, 15~43℃), 外気湿球温度(暖房, -20~15℃), 運転時部分負荷率(0.3~1)

### Parameters:

定格条件:

| name                | type  | description           |
| ------------------- | ----- | --------------------- |
| rated_capacity_c    | float | 定格冷房能力 [kW]     |
| rated_input_power_c | float | 定格冷房消費電力 [kW] |
| rated_capacity_h    | float | 定格暖房能力 [kW]     |
| rated_input_power_h | float | 定格暖房消費電力 [kW] |

計算条件:

| name            | type  | description               |
| --------------- | ----- | ------------------------- |
| odb             | float | 外気乾球温度 [℃]          |
| owb             | float | 外気湿球温度 [℃]          |
| indoor_capacity | float | 室内機冷房(暖房)能力 [kW] |

## pv.VariableRefrigerantFlowESS.cal_c(odb, indoor_capacity)

冷房時の室内機冷房能力(indoor_capacity)と外気乾球温度(odb)から、運転時の冷凍能力・電力消費量・COPを算出する

### returns:

冷凍能力(capacity)・電力消費量(input_power)・COP(cop)

## pv.VariableRefrigerantFlowESS.cal_h(owb, indoor_capacity)

暖房の定格値(rated_capacity, rated_input_power, indoor_capacity)と外気湿球温度(owb)により、運転時の暖房能力・電力消費量・COPを算出する

### returns:

暖房能力(capacity)・電力消費量(input_power)・COP(cop)

## **サンプルコード**

```python
import phyvac as pv   # 必要なモジュールのインポート

# 機器vrfの定義
vrf = pv.VariableRefrigerantFlowESS(rated_capacity_c=31.6548, rated_input_power_c=9.73, rated_capacity_h=37.5, rated_input_power_h=10.59)  
# 冷房の計算
# 定格条件
vrf.cal_c(odb=35, indoor_capacity=31.6548) 
print(vrf.capacity_c, vrf.input_power_c, vrf.cop_c)
```

> 結果
>
> 31.654799999999998 9.73 3.253319630010277

```python
# 室内機の容量が室外機より小さい場合
vrf.cal_c(odb=35, indoor_capacity=31.6548*0.8)
print(vrf.capacity_c, vrf.input_power_c, vrf.cop_c)
```

> 結果
>
> 25.323840000000004 6.815787160000003 3.715468133837676

```python
# 外気乾球温度が変化し、室内機の容量が室外機より小さい場合
vrf.cal_c(odb=32, indoor_capacity=31.6548*0.7)
print(vrf.capacity_c, vrf.input_power_c, vrf.cop_c)
vrf.cal_c(odb=40, indoor_capacity=31.6548)
print(vrf.capacity_c, vrf.input_power_c, vrf.cop_c)
```

> 結果
>
> 22.15836 5.353946481437806 4.138696581451326
>
> 31.259114999999998 10.351747000000001 3.0196946467103567

```python
# 暖房の計算
# 定格条件
vrf.cal_h(owb=6, indoor_capacity=37.5)
37.5 10.59 3.5410764872521248
```

> 結果
>
> 35.625 12.719999999999999 2.8007075471698117

```python
# 室内機の容量が室外機より小さい場合
vrf.cal_h(owb=6, indoor_capacity=37.5*0.7)
print(vrf.capacity_h, vrf.input_power_h, vrf.cop_h)
```

> 結果
>
> 26.25 6.238431329999999 4.207788562769994

```python
# 外気湿球温度が変化し、室内機の容量が室外機より小さい場合
vrf.cal_h(owb=10, indoor_capacity=37.5*0.6) 
print(vrf.capacity_h, vrf.input_power_h, vrf.cop_h)
vrf.cal_h(owb=0, indoor_capacity=37.5*0.9)  
print(vrf.capacity_h, vrf.input_power_h, vrf.cop_h)
```

> 結果
>
> 22.5 4.8032810492285725 4.684298039069272
>
> 28.575 9.776688 2.9227689377016017