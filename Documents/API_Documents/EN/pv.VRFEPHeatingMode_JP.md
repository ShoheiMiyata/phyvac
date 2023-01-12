## pv.VRFEPHeatingMode(rated_capacity=37.5, rated_input_power=10.59, length=10, height=5)

「EnergyPlus・System Curve based VRF Model」に基づいたビルマルモデル

定格暖房能力37.5kW、定格暖房消費電力10.59kWの室外機の各性能曲線を用いて暖房の計算をしている。仕様が異なる室外機の場合は、計算精度を保証するため、「equipment_spec.xlsx」というエクセルファイルに新たな曲線データを入力する必要がある。

暖房時の能力・消費電力・COPの計算

### Parameters:

定格条件

| name              | type  | description                |
| ----------------- | ----- | -------------------------- |
| rated_capacity    | float | 定格暖房能力 [kW]          |
| rated_input_power | float | 定格暖房消費電力 [kW]      |
| length            | float | 配管相当長 [m]             |
| height            | float | 室内機と室外機の高度差 [m] |

計算条件

| name            | type  | description                     |
| --------------- | ----- | ------------------------------- |
| idb             | float | 室内乾球温度 [℃]                |
| owb             | float | 室外湿球温度 [℃]                |
| indoor_capacity | float | 室内ユニットの合計暖房能力 [kW] |

## pv.VRFEPHeatingMode.get_cr_correction()

室内外機の容量が一致でない場合、暖房能力補正係数を計算する

### returns:

暖房能力補正係数(cr_correction_factor)

## pv.VRFEPHeatingMode.get_eirfplr()

室内外機の容量が一致でない場合、暖房消費電力補正係数を計算する

### returns:

暖房消費電力補正係数(eirfplr)

## pv.VRFEPHeatingMode.get_piping_correction()

配管相当長と高度差を考える場合、暖房能力補正係数を計算する

### returns:

暖房能力補正係数(piping_correction)

## pv.VRFEPHeatingMode.get_defrost_correction(owb)

室外湿球温度が低く、霜取補正を考える場合、霜取補正係数を計算する

### returns:

暖房能力補正係数(defrost__correction)

## pv.VRFEPHeatingMode.cal(idb, owb)

室内ユニットの合計容量と室外機容量が等しい場合、室内乾球温度・室外湿球温度から運転時の暖房能力・電力消費量・COPを算出する

### returns:

暖房能力(capacity)・電力消費量(input_power)・COP(cop)

## pv.VRFEPHeatingMode.cal_pl(idb, owb, indoor_capacity)

室内ユニットの合計容量と室外機容量が一致でない場合、室内乾球温度・室外湿球温度と室内ユニットの合計容量から運転時の暖房能力・電力消費量・COPを算出する

### returns:

暖房能力(capacity)・電力消費量(input_power)・COP(cop)

## pv.VRFEPHeatingMode.cal_loss(iwb, odb, indoor_capacity)

室外機から室内機までのパイプの相当長と機器の高度差による損失、霜取補正を考える場合、室内乾球温度・室外湿球温度と室内ユニットの合計容量から運転時の暖房能力・電力消費量・COPを算出する

### returns:

暖房能力(capacity)・電力消費量(input_power)・COP(cop)

## サンプルコード

```python
import phyvac as pv   # 必要なモジュールのインポート

# デフォルト値で機器vrf_hを定義
vrf_h = pv.VRFEPHeatingMode()
# 室内外機容量が等しい定格条件の場合
print(vrf_h.cal(idb=20, owb=6))
print(vrf_h.cal_pl(idb=20, owb=6, indoor_capacity=37.5))
# 同じ条件で配管損失を考えた場合(この温度で霜取補正は必要ない)
print(vrf_h.cal_loss(idb=20, owb=6, indoor_capacity=37.5))
```

> 結果
>
> 37.47272054680003, 10.454258707058129, 3.584445496982063
> 37.47272054680003, 10.454258707058129, 3.584445496982063
> 37.31888159104988, 10.454258707058129, 3.569730062816818

```python
# 室内機容量が室外機容量により小さい場合
print(vrf_h.cal_pl(idb=19, owb=10, indoor_capacity=25))
print(vrf_h.cal_loss(idb=19, owb=10, indoor_capacity=25))
# この場合、その温度条件下の室外機暖房能力は配管損失を考えて計算しても、要求された室内容量を提供できるため、同じ計算結果になるのである。
```

> 結果
>
> 25, 6.627828562806757, 3.771974450318761
> 25, 6.627828562806757, 3.771974450318761

```python
# 室内外の温度を変え、室内外機容量も一致でない場合
print(vrf_h.cal_pl(idb=21, owb=7, indoor_capacity=30))
print(vrf_h.cal_loss(idb=25, owb=-5, indoor_capacity=40))
```

> 結果
>
> 30, 7.8735971345415665, 3.810202565278535
> 25.930093068323906, 10.040968673919089, 2.582429435884609