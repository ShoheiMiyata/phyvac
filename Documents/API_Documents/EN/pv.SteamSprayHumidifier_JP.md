## pv.SteamSprayHumidifier(spec_table=pd.read_excel('EquipmentSpecTable.xlsx', sheet_name='SteamSprayHumidifier', header=None)
Calculation of outlet conditions for steam atomizing humidifiers

### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|area|float|Humidifier area[m2]|
|dp|float|Pressure drop[Pa]|
|sat_eff|float|Saturation efficiency[-]|
|an|float|Wind speed[m/s] - Coefficient of the nth order of pressure drop[Pa]|
|tdb_air_in|float|Inlet air dry bulb temperature['C]|
|w_air_in|float|Inlet air absolute humidity[kg/kg']|
|flowrate_air_in|float|Inlet air mass flow rate[kg/s]|
|t_steam_in|float|Inlet steam temperature['C]|
|flowrate_steam_in|float|Inlet water vapor flow[kg/s]|
|tdb_air_out|float|Outlet air dry bulb temperature['C]|
|w_air_out|float|Outlet air absolute humidity[kg/kg']|
|flowrate_air_out|float|Outlet air mass flow rate[kg/s]|
  
## pv.SteamSprayHumidifier.cal(tdb_air_in, w_air_in, flowrate_air_in, flowrate_steam_in, t_steam_in)
Take Inlet dry ball temperature: tdb_air_in、Inlet absolute humidity: w_air_in、Air mass flow rate: flowrate_air_in、Inlet vapor mass flow rate、Indoor vapor temperature:t_steam_in as input value to calculate outlet conditions and pressure drop.
  
### returns:
Outlet air temperaturet: db_air_out、Outlet absolute humidity: w_air_out、humidification volume: flowrate_water_add、Pressure drop: dp

  
## Sample codes  
```
import phyvac as pv
import pandas as pd

HUM = SprayHumidifier() # Definition of HUM(Use spec_table=pd.read_excel('EquipmentSpecTable.xlsx', sheet_name='SteamSprayHumidifier'） 
# The input characteristics are as follows
# HUM.area = 0.675
# HUM.dp = 45
# HUM.sat_eff = 0.6

# Calculate outlet conditions by the following parameters:
# Inlet dry ball temperature = 16[℃], Inlet air absolute humidity = 0.007[kg/kg’], Air mass flow rate = 1.68[kg/s], Humidifying steam flow rate = 0.0305[kg/s], Humidifying steam temperature = 40[℃]
HUM = SteamSprayHumidifier()
HUM.cal(16, 0.007, 1.68, 0.0305, 40)
print(HUM.tdb_air_out, HUM.w_air_out, HUM.flowrate_air_out, HUM.dp)

```
> Result
> 16.776373404224994, 0.007178393753416995, 1.6802976181784912, 45.0
