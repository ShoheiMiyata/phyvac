## **pv.AbsorptionChillerESS(rated_capacity_c, rated_input_fuel_c, power_c, rated_capacity_h, rated_input_fuel_h, power_h)**

省エネルギー基準に基づいた吸収式冷温水発生機モデル

冷(暖)房能力・燃料消費量・COPの計算・冷(温)水出口温度

計算できる範囲: 冷却水入口温度(20℃～32℃), 冷水出口温度(5℃～12℃), 温水出口温度(45℃～60℃), 冷房運転時部分負荷(0.2～1), 暖房運転時部分負荷(0.1～1)

### **Parameters:**

定格条件:

| name               | type  | description                           |
| ------------------ | ----- | ------------------------------------- |
| rated_capacity_c   | float | 定格冷房能力 [kW]                     |
| rated_input_fuel_c | float | 定格冷房燃料(都市ガス13A)消費量 [Nm3] |
| power_c       　　 | float | 冷房消費電力 [kW]                     |
| rated_capacity_h   | float | 定格暖房能力 [kW]                     |
| rated_input_fuel_h | float | 定格暖房燃料(都市ガス13A)消費量 [Nm3] |
| power_h   　　     | float | 暖房消費電力 [kW]                     |

計算条件:

| name       | type  | description             |
| ---------- | ----- | ----------------------- |
| tin_cd     | float | 冷却水入口温度 [℃]      |
| tin_ch     | float | 冷水入口温度 [℃]        |
| tout_ch_sv | float | 冷水出口温度設定値 [℃]  |
| tin_h      | float | 温水入口温度 [℃]        |
| tout_h_sv  | float | 温水出口温度設定値 [℃]  |
| g          | float | 冷水(温水)流量 [m3/min] |

## **pv.AbsorptionChillerESS.cal_c(g, tin_cd, tin_ch, tout_ch_sv)**

冷房時の冷却水入口温度(tin_cd)・冷水入口温度(tin_ch)・冷水出口温度設定値(tout_ch_sv)・冷水流量(g)から、運転時の冷凍能力・燃料消費量・COP・冷水出口温度を算出する

### returns:

冷凍能力(capacity)・燃料消費量(input_fuel)・COP(cop)・冷水出口温度(tout_ch)・冷房消費電力(power_c)

## **pv.AbsorptionChillerESS.cal_h(g, tin_h, tout_h_sv)**

暖房時の温水入口温度(tin_h)・温水出口温度設定値(tout_h_sv)・温水流量(g)から、運転時の暖房能力・燃料消費量・COP・温水出口温度を算出する

### **returns:**

暖房能力(capacity)・燃料消費量(input_fuel)・COP(cop)・温水出口温度(tout_h)・暖房消費電力(power_h)

## **サンプルコード**

```python
import phyvac as pv   # 必要なモジュールのインポート

# 機器acの定義
ac = pv.AbsorptionChillerESS(rated_capacity_c=527, rated_input_fuel_c=32.4, power_c=5.1, rated_capacity_h=527, rated_input_fuel_h=48.4, power_h=4.3) 
# 冷房の計算
# 定格条件の場合
ac.cal_c(g=1.512, tin_cd=32, tin_ch=12, tout_ch_sv=7)   
print(ac.capacity_c, ac.input_fuel_c, ac.cop_c, ac.tout_ch, ac.power_c)
```

> 結果
>
> 527 32.394864983159664 1.422624524783494 7.009991363359863 5.1

```python
# 負荷率を小さくし、冷却水温度と冷水入口温度も低下させた場合
ac.cal_c(g=1.512, tin_cd=27, tin_ch=10.75, tout_ch_sv=7)   
print(ac.capacity_c, ac.input_fuel_c, ac.cop_c, ac.tout_ch, ac.power_c)
ac.cal_c(g=1.512, tin_cd=22, tin_ch=9.5, tout_ch_sv=7)   
print(ac.capacity_c, ac.input_fuel_c, ac.cop_c, ac.tout_ch, ac.power_c)
```

> 結果
>
> 396.041398704 22.4563450582688 1.5329190723298747 7 5.1
>
> 264.02759913600005 14.093717647411484 1.609474755726364 7 5.1

```python
# 冷水流量を小さくし、冷水入口温度が変化した場合
ac.cal_c(g=1.512*0.75, tin_cd=27, tin_ch=12, tout_ch_sv=7)   
print(ac.capacity_c, ac.input_fuel_c, ac.cop_c, ac.tout_ch, ac.power_c)
ac.cal_c(g=1.512*0.86, tin_cd=32, tin_ch=10, tout_ch_sv=5)
print(ac.capacity_c, ac.input_fuel_c, ac.cop_c, ac.tout_ch, ac.power_c)
```

> 結果
>
> 396.0413987039999 22.45634505826879 1.5329190723298747 7 5.1
>
> 454.12747051391995 28.309221484851015 1.4000503073795854 5 5.1

```python
# 冷水流量を大きくし、冷水出口温度を確認する場合
ac.cal_c(g=1.512*1.2, tin_cd=32, tin_ch=12, tout_ch_sv=7)   
print(ac.capacity_c, ac.input_fuel_c, ac.cop_c, ac.tout_ch, ac.power_c)
```

> 結果
>
> 527 32.05103721020772 1.437673412587789 7.841659469466553 5.1

```python
# 暖房の計算
# 定格条件の場合
ac.cal_h(g=1.512, tin_h=45, tout_h_sv=50)  
print(ac.capacity_h, ac.input_fuel_h, ac.cop_h, ac.tout_h, ac.power_h)
```

> 結果
>
> 522.32712588 47.97084040340038 0.9578632618385874 50 4.3

```python
# 負荷率を小さくし、温水入口温度も高くさせた場合
ac.cal_h(g=1.512, tin_h=47, tout_h_sv=50)  
print(ac.capacity_h, ac.input_fuel_h, ac.cop_h, ac.tout_h, ac.power_h)
```

> 結果
>
> 313.396275528 28.782504242040226 0.952854106009719 50 4.3

```python
# 温水流量を小さくし、温水入口温度が変化した場合
ac.cal_h(g=1.512*0.8, tin_h=43, tout_h_sv=48)   
print(ac.capacity_h, ac.input_fuel_h, ac.cop_h, ac.tout_h, ac.power_h)
```

> 結果
>
> 417.861700704 38.3766723227203 0.9559786687157514 48 4.3

```python
# 温水流量を大きくし、温水出口温度を確認する場合
ac.cal_h(g=1.512*1.2, tin_h=45, tout_h_sv=50)   
print(ac.capacity_h, ac.input_fuel_h, ac.cop_h, ac.tout_h, ac.power_h)
```

> 結果
>
> 527 48.4 0.9579302405428878 49.203942748778104 4.3
