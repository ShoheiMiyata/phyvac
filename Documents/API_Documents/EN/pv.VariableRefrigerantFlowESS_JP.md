## pv.VariableRefrigerantFlowESS(rated_capacity_c, rated_input_power_c, rated_capacity_h, rated_input_power_h)

省エネルギー基準に基づいたビルマルモデル

Calculating cooling capacity, power consumption, COP

Calculation range: outdoor dry bulb temperature(cooling, 15～43℃), outdoor wet bulb temperature(heating, -20～15℃), operating partial load ratio(0.3～1)

### Parameters:

Rated conditions:

| name                | type  | description                                                   |
| ------------------- | ----- | ------------------------------------------------------------- |
| rated_capacity_c    | float | Rated cooling capacity [kW]                                   |
| rated_input_power_c | float | Rated consumption of electricity for cooling [kW]             |
| rated_capacity_h    | float | Rated heating capacity [kW]                                   |
| rated_input_power_h | float | Rated consumption of electricity for heating [kW]             |

Calculation conditions:

| name            | type  | description                                 |
| --------------- | ----- | ------------------------------------------- |
| odb             | float | outdoor dry bulb temperature [℃]           |
| owb             | float | outdoor wet bulb temperature [℃]           |
| indoor_capacity | float | Indoor unit cooling (heating) capacity [kW] |

## pv.VariableRefrigerantFlowESS.cal_c(odb, indoor_capacity)

Calculate the cooling capacity of outdoor unit, power consumption, COP when opterating based on total cooling capacity of indoor unit and outdoor dry temperature

### returns:

Cooling capacity(capacity)・power consumption(input_power)・COP(cop)

## pv.VariableRefrigerantFlowESS.cal_h(owb, indoor_capacity)

Calculate the heating capacity, electricity consumption, and COP of the outdoor unit during operation based on the total heating capacity of the indoor unit (indoor_capacity) and outdoor wet bulb temperature (owb)

### returns:

Heating capacity (capacity), power consumption (input_power), COP (cop)

## **Sample codes**

```python
import phyvac as pv

# Definition of vrf
vrf = pv.VariableRefrigerantFlowESS(rated_capacity_c=31.6548, rated_input_power_c=9.73, rated_capacity_h=37.5, rated_input_power_h=10.59)  
# Calculation of cooling
# Rated conditions
vrf.cal_c(odb=35, indoor_capacity=31.6548) 
print(vrf.capacity_c, vrf.input_power_c, vrf.cop_c)
```

> Result
>
> 31.654799999999998 9.73 3.253319630010277

```python
# When the capacity of indoor unit is smaller than that of outdoor unit
vrf.cal_c(odb=35, indoor_capacity=31.6548*0.8)
print(vrf.capacity_c, vrf.input_power_c, vrf.cop_c)
```

> Result
>
> 25.323840000000004 6.815787160000003 3.715468133837676

```python
# When the outdoor dry bulb temperature changes and the capacity of the indoor unit is smaller than that of the outdoor unit
vrf.cal_c(odb=32, indoor_capacity=31.6548*0.7)
print(vrf.capacity_c, vrf.input_power_c, vrf.cop_c)
vrf.cal_c(odb=40, indoor_capacity=31.6548)
print(vrf.capacity_c, vrf.input_power_c, vrf.cop_c)
```

> Result
>
> 22.15836 5.353946481437806 4.138696581451326
>
> 31.259114999999998 10.351747000000001 3.0196946467103567

```python
# Calculation of heating
# Rated conditions
vrf.cal_h(owb=6, indoor_capacity=37.5)
print(vrf.capacity_h, vrf.input_power_h, vrf.cop_h)
```

> Result
>
> 37.5 10.59 3.5410764872521248

```python
# When the capacity of indoor unit is smaller than that of outdoor unit
vrf.cal_h(owb=6, indoor_capacity=37.5*0.7)
print(vrf.capacity_h, vrf.input_power_h, vrf.cop_h)
```

> Result
>
> 26.25 6.238431329999999 4.207788562769994

```python
# When the outdoor wet bulb temperature changes and the capacity of the indoor unit is smaller than that of the outdoor unit
vrf.cal_h(owb=10, indoor_capacity=37.5*0.6) 
print(vrf.capacity_h, vrf.input_power_h, vrf.cop_h)
vrf.cal_h(owb=-10, indoor_capacity=37.5)  
print(vrf.capacity_h, vrf.input_power_h, vrf.cop_h)
```

> Result
>
> 22.5 4.8032810492285725 4.684298039069272
>
> 22.2 8.421168 2.636213883869791
