## pv.SprayHumidifier()
気化式加湿器の出口状態の計算

<img src="https://user-images.githubusercontent.com/78840483/147629436-70da761d-3b0e-4b91-8e81-bd44aa0aec5f.png" width=40%>
<img src="https://user-images.githubusercontent.com/78840483/147629938-d30c39e5-74e1-4b77-87dc-d0d1ba632cc6.png" width=40%>

### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|d|float|Humidifying element thickness[m]|
|area|float|Humidifier area[m2]|
|an|float|wind speed[m/s] - Coefficient of the nth order of pressure drop [Pa]|
|tdb_air_in|float|Inlet air dry bulb temperature['C]|
|w_air_in|float|Inlet air absolute humidity[kg/kg']|
|flowrate_air_in|float|Inlet air mass flow rate[kg/s]|
|flowrate_water_req|float|Required humidifying mass flow rate[kg/s]|
|tdb_air_out|float|Outlet air dry bulb temperature['C]|
|twb_air_out|float|Outlet air wet bulb temperature['C]|
|w_air_out|float|Outlet air absolute humidity[kg/kg']|
|flowrate_air_out|float|Outlet air mass flow rate[kg/s]|
|flowrate_water_add|float|Humidifying mass flow rate[kg/s]|
|dp|float|Pressure drop[Pa]|

  
## pv.SprayHumidifier.cal(tdb_air_in, w_air_in, flowrate_air_in, flowrate_water_req)
Take Inlet dry ball temperature: tdb_air_in、Inlet absolute humidity: w_air_in、Air mass flow rate: flowrate_air_in、Required humidification volume: flowrate_water_req as input value to calculate outlet conditions and pressure drop.
  
### returns:
Outlet dry ball temperature: tdb_air_out、Outlet wet bulb temperature: twb_air_out、Outlet absolute humidity: w_air_out、humidification volume: flowrate_water_add、pressure drop dp

  
## Sample codes
```
import phyvac as pv
import math
import pandas as pd

HUM = SprayHumidifier() # Definition of HUM (Use spec_table=pd.read_excel('EquipmentSpecTable.xlsx', sheet_name='SprayHumidifier'）
# The input characteristics are as follows
# HUM.d = 0.075
# HUM.area = 0.675
# HUM.rh_border = 95
# HUM.a2 = 4.2143
# HUM.a1 = -2.1643
# HUM.a0 = 2.1286

# Calculate outlet conditions by the following parameters:
# Inlet dry ball temperature = 16[℃], Inlet air absolute humidity = 0.007[kg/kg’], Air mass flow rate = 1.68[kg/s], Required humidification flow rate = 0.001[kg/s]
HUM.cal(16, 0.007, 4675 * 1.293 / 3600, 0.001))
print(HUM.tdb_air_out, HUM.twb_air_out, HUM.w_air_out, HUM.flowrate_water_add, HUM.dp)

```
> Result  
> 14.522529672178925, 13.96484375, 0.007595555665843642, 0.0006339037632936271, 13.56303095776389
