## pv.VariableRefrigerantFlowEP(rated_capacity=31.6548, rated_input_power=9.73, length=10, height=5)

「EnergyPlus・System Curve based VRF Model」に基づいたビルマルモデル

Cooling calculations are made using the respective performance curves of an outdoor unit with a rated cooling capacity of 31.6548 kW and a rated cooling power consumption of 9.73 kW. For outdoor units with different specifications, new curve data must be entered in an Excel file called "equipment_spec.xlsx" to guarantee calculation accuracy.

Calculation of capacity, electricity consumption, and COP for cooling

### Parameters:

Rated conditions

| name              | type  | description                                                             |
| ----------------- | ----- | ----------------------------------------------------------------------- |
| rated_capacity    | float | Rated cooling capacity [kW]                                             |
| rated_input_power | float | Rated consumption of electricity for cooling [kW]                       |
| length            | float | Pipes length [m]                                                        |
| height            | float | Difference in height between indoor unit and outdoor unit [m]           |

Calculation conditions

| name            | type  | description                                     |
| --------------- | ----- | ----------------------------------------------- |
| iwb             | float | Indoor wet bulb temperature [℃]                |
| odb             | float | Outdoor dry bulb temperature [℃]               |
| indoor_capacity | float | Total cooling capacity of indoor units [kW]     |

## pv.VariableRefrigerantFlowEP.get_cr_correction()

Calculate the cooling capacity correction factor when the capacities of indoor and outdoor units do not match.

### returns:

Cooling Capacity Correction Factor(cr_correction_factor)

## pv.VariableRefrigerantFlowEP.get_eirfplr()

Calculate the cooling electricity consumption correction factor when the capacities of indoor and outdoor units do not match.

### returns:

Cooling electricity consumption correction factor(eirfplr)

## pv.VariableRefrigerantFlowEP.get_piping_correction()

Calculate cooling capacity correction factor when considering pipe equivalent length and altitude difference

### returns:

Cooling capacity correction factor by pipe equivalent length (piping_correction_length), cooling capacity correction factor by height difference (piping_correction_height)

## pv.VariableRefrigerantFlowEP.cal(iwb, odb)

When the total indoor unit capacity and outdoor unit capacity are equal, the cooling capacity, power consumption, and COP during operation are calculated from the indoor wet bulb temperature and outdoor dry bulb temperature.

### returns:

Cooling capacity(capacity)・Power consumption(input_power)・COP(cop)

## pv.VariableRefrigerantFlowEP.cal_pl(iwb, odb, indoor_capacity)

If the total capacity of the indoor unit and the capacity of the outdoor unit do not match, the cooling capacity, power consumption, and COP during operation are calculated from the indoor wet bulb temperature, outdoor dry bulb temperature, and total capacity of the indoor unit.

### returns:

Cooling capacity(capacity)・Power consumption(input_power)・COP(cop)

## pv.VariableRefrigerantFlowEP.cal_loss(iwb, odb, indoor_capacity)

When considering the equivalent length of pipe from the outdoor unit to the indoor unit and the loss due to the difference in height of the equipment, the cooling capacity, power consumption, and COP during operation are calculated from the indoor wet bulb temperature, outdoor dry bulb temperature, and total indoor unit capacity.

### returns:

Cooling capacity(capacity)・Power consumption(input_power)・COP(cop)

## **Sample codes**

``` python
import phyvac as pv 

# Define equipment vrf with default values
vrf = pv.VariableRefrigerantFlowEP() 
# For rated conditions where indoor and outdoor unit capacities are equal
print(vrf.cal(19, 35)) 
print(vrf.cal_pl(iwb=19, odb=35, indoor_capacity=31.6548))
# Considering losses by pipes under the same conditions
print(vrf.cal_loss(iwb=19, odb=35, indoor_capacity=31.6548))   
```

> Result
>
> 31.499145265405, 9.745514177957604, 3.2321686357657495
>31.499145265405, 9.745514177957604, 3.2321686357657495
> 30.769564819365403, 9.745514177957604, 3.1573054286822524

``` python
# When the indoor unit capacity is smaller than the outdoor unit capacity
print(vrf.cal_pl(iwb=25, odb=35, indoor_capacity=25))
print(vrf.cal_loss(iwb=25, odb=35, indoor_capacity=25))
# この場合、その温度条件下の室外機冷凍能力は配管損失を考えて計算しても、要求された室内容量を提供できるため、同じ計算結果になるのである。
```

> Result
>
> 25, 7.202408108584883, 3.4710612927086633
>25, 7.202408108584883, 3.4710612927086633

``` python
# When indoor and outdoor temperatures are changed and indoor and outdoor unit capacities are not matched
print(vrf.cal_pl(iwb=19, odb=40, indoor_capacity=35))
print(vrf.cal_loss(iwb=26, odb=33, indoor_capacity=20))
```

> Result
>
> 31.437017072915726, 10.529153616036925, 2.985711693391394
>20, 5.214505493261637, 3.835454776266836
