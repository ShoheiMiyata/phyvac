## **pv.AbsorptionChillerESS(rated_capacity_c, rated_input_fuel_c, power_c, rated_capacity_h, rated_input_fuel_h, power_h)**

Absorption chiller/heater generator model based on energy conservation standards

Cooling (heating) capacity, fuel consumption, COP calculation, cold (hot) water outlet temperature

Calculation range: Cooling water inlet temperature (20°C to 32°C), chilled water outlet temperature (5°C to 12°C), hot water outlet temperature (45°C to 60°C), partial load during cooling operation (0.2 to 1), partial load during heating operation (0.1 to 1)

### **Parameters:**

Rated conditions:

| name               | type  | description                                                           |
| ------------------ | ----- | ----------------------------------------------------------------------|
| rated_capacity_c   | float | Rated cooling capacity [kW]                                           |
| rated_input_fuel_c | float | Rated consumption of fuel for cooling(urban gas 13A) [Nm3]            |
| power_c       　　 | float | Rated consumption of electricity for cooling [kW]                     |
| rated_capacity_h   | float | Rated heating capacity [kW]                                           |
| rated_input_fuel_h | float | Rated consumption of fuel for heating(urban gas 13A) [Nm3]            |
| power_h   　　     | float | Rated consumption of electricity for heating [kW]                     |

Calculation condition:

| name       | type  | description                                    |
| ---------- | ----- | -----------------------------------------------|
| tin_cd     | float | Cooling water inlet temperature [℃]           |
| tin_ch     | float | Chilled water inlet temperature [℃]           |
| tout_ch_sv | float | Chilled water outlet temperature setpoint [℃] |
| tin_h      | float | Heating water inlet temperature [℃]           |
| tout_h_sv  | float | Heating water outlet temperature setpoint [℃] |
| g          | float | Chilled water (heating water) flow [m3/min]    |

## **pv.AbsorptionChillerESS.cal_c(g, tin_cd, tin_ch, tout_ch_sv)**

Calculate the cooling capacity, fuel consumption, COP, and chilled water outlet temperature during operation from the cooling water inlet temperature (tin_cd), chilled water inlet temperature (tin_ch), chilled water outlet temperature setpoint (tout_ch_sv), and chilled water flow rate (g) during cooling

### returns:

Cooling capacity・Fuel consumption (input_fuel)・COP (cop)・Chilled water outlet temperature (tout_ch)・Consumption of electricity for cooling(power_c)

## **pv.AbsorptionChillerESS.cal_h(g, tin_h, tout_h_sv)**

Calculate the heating capacity, fuel consumption, COP, and heating water outlet temperature during operation from the heating water inlet temperature (tin_h),  heating water outlet temperature setpoint (ttout_h_sv), and heating water flow rate (g) during heating


### **returns:**

Heating capacity (capacity)・Fuel consumption (input_fuel)・COP(cop)・Heating water outlet temperature(tout_h)・Consumption of electricity for heating (power_h)

## **Sample codes**

```python
import phyvac as pv

# Definition of ac
ac = pv.AbsorptionChillerESS(rated_capacity_c=527, rated_input_fuel_c=32.4, power_c=5.1, rated_capacity_h=527, rated_input_fuel_h=48.4, power_h=4.3) 
# Cooling calculation
# Rated conditions
ac.cal_c(g=1.512, tin_cd=32, tin_ch=12, tout_ch_sv=7)   
print(ac.capacity_c, ac.input_fuel_c, ac.cop_c, ac.tout_ch, ac.power_c)
```

> Result
>
> 527 32.394864983159664 1.422624524783494 7.009991363359863 5.1

```python
# When the load factor is reduced and the cooling water temperature and chilled water inlet temperature are also reduced
ac.cal_c(g=1.512, tin_cd=27, tin_ch=10.75, tout_ch_sv=7)   
print(ac.capacity_c, ac.input_fuel_c, ac.cop_c, ac.tout_ch, ac.power_c)
ac.cal_c(g=1.512, tin_cd=22, tin_ch=9.5, tout_ch_sv=7)   
print(ac.capacity_c, ac.input_fuel_c, ac.cop_c, ac.tout_ch, ac.power_c)
```

> Result
>
> 396.041398704 22.4563450582688 1.5329190723298747 7 5.1
>
> 264.02759913600005 14.093717647411484 1.609474755726364 7 5.1

```python
# When the chilled water flow rate is reduced and the chilled water inlet temperature changes
ac.cal_c(g=1.512*0.75, tin_cd=27, tin_ch=12, tout_ch_sv=7)   
print(ac.capacity_c, ac.input_fuel_c, ac.cop_c, ac.tout_ch, ac.power_c)
ac.cal_c(g=1.512*0.86, tin_cd=32, tin_ch=10, tout_ch_sv=5)
print(ac.capacity_c, ac.input_fuel_c, ac.cop_c, ac.tout_ch, ac.power_c)
```

> Result
>
> 396.0413987039999 22.45634505826879 1.5329190723298747 7 5.1
>
> 454.12747051391995 28.309221484851015 1.4000503073795854 5 5.1

```python
# When increasing chilled water flow rate and check chilled water outlet temperature
ac.cal_c(g=1.512*1.2, tin_cd=32, tin_ch=12, tout_ch_sv=7)   
print(ac.capacity_c, ac.input_fuel_c, ac.cop_c, ac.tout_ch, ac.power_c)
```

> Result
>
> 527 32.05103721020772 1.437673412587789 7.841659469466553 5.1

```python
# Heating calculation
# Rated conditions
ac.cal_h(g=1.512, tin_h=45, tout_h_sv=50)  
print(ac.capacity_h, ac.input_fuel_h, ac.cop_h, ac.tout_h, ac.power_h)
```

> Result
>
> 522.32712588 47.97084040340038 0.9578632618385874 50 4.3

```python
# When the load factor is reduced and the hot water inlet temperature is increased
ac.cal_h(g=1.512, tin_h=47, tout_h_sv=50)  
print(ac.capacity_h, ac.input_fuel_h, ac.cop_h, ac.tout_h, ac.power_h)
```

> Result
>
> 313.396275528 28.782504242040226 0.952854106009719 50 4.3

```python
# When hot water flow rate is reduced and hot water inlet temperature changes
ac.cal_h(g=1.512*0.8, tin_h=43, tout_h_sv=48)   
print(ac.capacity_h, ac.input_fuel_h, ac.cop_h, ac.tout_h, ac.power_h)
```

> Result
>
> 417.861700704 38.3766723227203 0.9559786687157514 48 4.3

```python
# To increase hot water flow rate and check hot water outlet temperature
ac.cal_h(g=1.512*1.2, tin_h=45, tout_h_sv=50)   
print(ac.capacity_h, ac.input_fuel_h, ac.cop_h, ac.tout_h, ac.power_h)
```

> Result
>
> 527 48.4 0.9579302405428878 49.203942748778104 4.3
