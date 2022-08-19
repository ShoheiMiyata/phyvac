## pv.VariableRefrigerantFlowEP(rated_capacity=31.6548, rated_input_power=9.73, length=10, height=5)

「EnergyPlus・System Curve based VRF Model」に基づいたビルマルモデル

定格冷房能力31.6548kW、定格冷房消費電力9.73kWの室外機の各性能曲線を用いて冷房の計算をしている。仕様が異なる室外機の場合は、計算精度を保証するため、「equipment_spec.xlsx」というエクセルファイルに新たな曲線データを入力する必要がある。

冷房時の能力・消費電力・COPの計算

### Parameters:

定格条件

| name              | type  | description                |
| ----------------- | ----- | -------------------------- |
| rated_capacity    | float | 定格冷房能力 [kW]          |
| rated_input_power | float | 定格冷房消費電力 [kW]      |
| length            | float | 配管相当長 [m]             |
| height            | float | 室内機と室外機の高度差 [m] |

計算条件

| name            | type  | description                     |
| --------------- | ----- | ------------------------------- |
| iwb             | float | 室内湿球温度 [℃]                |
| odb             | float | 室外乾球温度 [℃]                |
| indoor_capacity | float | 室内ユニットの合計冷房能力 [kW] |

## pv.VariableRefrigerantFlowEP.get_cr_correction()

室内外機の容量が一致でない場合、冷房能力補正係数を計算する

### returns:

冷房能力補正係数(cr_correction_factor)

## pv.VariableRefrigerantFlowEP.get_eirfplr()

室内外機の容量が一致でない場合、冷房消費電力補正係数を計算する

### returns:

冷房消費電力補正係数(eirfplr)

## pv.VariableRefrigerantFlowEP.get_piping_correction()

配管相当長と高度差を考える場合、冷房能力補正係数を計算する

### returns:

配管相当長による冷房能力補正係数(piping_correction_length), 高度差による冷房能力補正係数(piping_correction_height)

## pv.VariableRefrigerantFlowEP.cal(iwb, odb)

室内ユニットの合計容量と室外機容量が等しい場合、室内湿球温度・室外乾球温度から運転時の冷凍能力・電力消費量・COPを算出する

### returns:

冷凍能力(capacity)・電力消費量(input_power)・COP(cop)

## pv.VariableRefrigerantFlowEP.cal_pl(iwb, odb, indoor_capacity)

室内ユニットの合計容量と室外機容量が一致でない場合、室内湿球温度・室外乾球温度と室内ユニットの合計容量から運転時の冷凍能力・電力消費量・COPを算出する

### returns:

冷凍能力(capacity)・電力消費量(input_power)・COP(cop)

## pv.VariableRefrigerantFlowEP.cal_loss(iwb, odb, indoor_capacity)

室外機から室内機までのパイプの相当長と、機器の高度差による損失を考える場合、室内湿球温度・室外乾球温度と室内ユニットの合計容量から運転時の冷凍能力・電力消費量・COPを算出する

### returns:

冷凍能力(capacity)・電力消費量(input_power)・COP(cop)

## **サンプルコード**

``` python
import phyvac as pv   # 必要なモジュールのインポート

# デフォルト値で機器vrfを定義
vrf = pv.VariableRefrigerantFlowEP() 
# 室内外機容量が等しい定格条件の場合
print(vrf.cal(19, 35)) 
print(vrf.cal_pl(iwb=19, odb=35, indoor_capacity=31.6548))
# 同じ条件で配管損失を考えた場合
print(vrf.cal_loss(iwb=19, odb=35, indoor_capacity=31.6548))   
```

> 結果
>
> 31.499145265405, 9.745514177957604, 3.2321686357657495
>31.499145265405, 9.745514177957604, 3.2321686357657495
> 30.769564819365403, 9.745514177957604, 3.1573054286822524

``` python
# 室内機容量が室外機容量により小さい場合
print(vrf.cal_pl(iwb=25, odb=35, indoor_capacity=25))
print(vrf.cal_loss(iwb=25, odb=35, indoor_capacity=25))
# この場合、その温度条件下の室外機冷凍能力は配管損失を考えて計算しても、要求された室内容量を提供できるため、同じ計算結果になるのである。
```

> 結果
>
> 25, 7.202408108584883, 3.4710612927086633
>25, 7.202408108584883, 3.4710612927086633

``` python
# 室内外の温度を変え、室内外機容量も一致でない場合
print(vrf.cal_pl(iwb=19, odb=40, indoor_capacity=35))
print(vrf.cal_loss(iwb=26, odb=33, indoor_capacity=20))
```

> 結果
>
> 31.437017072915726, 10.529153616036925, 2.985711693391394
>20, 5.214505493261637, 3.835454776266836
