## Main code structure
The main code is structured as follows:
- read input files
- define equipment, branch and control
- time step calculation
  - input boundary condition such as outdoor air temperature, heat load, etc.
  - control equiment
  - flow balance calculation
  - temperature and power calculation
- save output files
## Code example - 1AHU_simpleAHU.py
The full code is uploaded [here](https://github.com/ShoheiMiyata/phyvac/tree/main/MainSample/1AHP_simpleAHU/miyata).  
  
First of all, import modules used in this program.
```
import phyvac as pv
import pandas as pd
import time
import copy
import numpy as np
import datetime
``` 
### read input files
Here, the input data is at 15-minute intervals, so it is converted to 1-minute intervals for the simulation.
```
input_data = pd.read_csv("Input15min.csv", index_col=0, parse_dates=True)
input_data = input_data.resample('1min').interpolate()
```
Create a data frame to store the calculation results.
```
output_data = input_data.drop(input_data.columns[[0, 1, 2, 3, 4]], axis=1)
output_data = output_data.assign(g_load=0.0, AHU_g=0.0, AHU_tin=0.0, AHU_tout=0.0, Vlv_AHU=0.0, dp_header=0.0, CP1_g=0.0, CP1_inv=0.0, CP1_pw=0.0,
                                 CP1_dp=0.0, CP1_ef=0.0, AHP1_g_ch=0.0, AHP1_tin_ch=0.0, AHP1_tout_ch=0.0, AHP1_COP=0.0,
                                 AHP1_pw=0.0, AHP1_pl=0.0, tdb=0.0)
```
### define equipment
`AHU`:air handling units, `Vlv_AHU`: valve for AHU, `ASHP1`: air source heat pump, `CP1`: chilled-water pump for ASHP1  
If the default value of the module is not suitable for the target equipment, input specification parameters.
```
AHU = pv.AHU_simple(kr=1000)
Vlv_AHU = pv.Valve(cv_max=40, r=100)
ASHP1 = pv.AirSourceHeatPump(spec_table=pd.read_excel('equipment_spec.xlsx', sheet_name='AirSourceHeatPump',encoding="SHIFT-JIS",header=None))
CP1 = pv.Pump(pg=[108.22, 37.32, -1543.39], eg=[0, 5.6657, -13.8139], r_ef=0.8)
```
### define branch  
The following loop can be regarded as two branches. `Branch_aAHUb` is the branch from point a through AHU to point b. `Branch_bASHP1a` is the branch from point b through ASHP1 to point a.  
In order to perform a flow balance calculation, it is necessary to set up a branch that does not have a pump but will always have a flow rate during operation. This applies no matter how complex the pipe network is.  
<img src="https://user-images.githubusercontent.com/27459538/111591618-0b44ad00-880b-11eb-83d8-9b713edc8672.png" width=30%>
```
Branch_aAHUb = pv.Branch01(valve=Vlv_AHU, kr_eq=AHU.kr, kr_pipe=1000)
Branch_bASHP1a = pv.Branch10(pump=CP1, kr_eq=ASHP1.kr_ch, kr_pipe=1000)
```
### define control
`PID_Vlv_AHU`: PI control for Vlv_AHU, `PID_CP1`: PI control for CP1  
If the default value of the module is not suitable for the target control, input control parameters.
```
PID_Vlv_AHU = pv.PID(kp=0.3, ti=400)
PID_CP1 = pv.PID(kp=0.3, ti=500, a_min=0)
```
### time step calculation: input boundary condition
`g_load`: flow load which is the set value of valve for AHU [m3/min], `q_load`: heat load [MJ/min], `t_supply_sv`: set value for supply chilled water ['C], `tdb`: outdoor air dry bulb temperature ['C], `rh`: relative humidity \[%](0~100)
```
current_time = datetime.datetime(2018, 8, 21, 0, 0)
for calstep in tqdm(range(24*60*4)):
    g_load = input_data.iat[calstep, 0]        # 負荷流量[m3/min]
    q_load = input_data.iat[calstep, 1]        # 負荷熱量[MJ/min]
    t_supply_sv = input_data.iat[calstep, 2]   # 供給水温設定値[℃]
    tdb = input_data.iat[calstep, 3]           # 外気乾球温度[℃]
    rh = input_data.iat[calstep, 4]            # 外気相対湿度[%](0~100)
```
### control pump and valve
The system is operated from 9:00 to 18:00.  
The valve for AHU is controled according to the load flow and the pump is controled to keep the differential pressure between point a and b to the set value (50 kPa).
```
    if current_time.hour >= 9 and current_time.hour < 18: # daytime
        CP1.inv = PID_CP1.control(sv=50, mv=-Branch_aAHUb.dp)
        Vlv_AHU.vlv = PID_Vlv_AHU.control(sv=g_load, mv=Vlv_AHU.g)
    else: # nighttime
        CP1.inv = 0
        Vlv_AHU.vlv = 0
```
### flow balance calculation  
The first step is to set the minimum (`g_min = 0.0`) and maximum flow rates (`g_max = 0.5`) for the branch where the flow always occurs (`Branch_aAHUb`). Give appropriate initial value to the variable for the convergence judgment (`g_eva = 0.5`).  
In the while sentense, we first assume flow rate for `Branch_aAHUb` (`g = (g_max + g_min) / 2`, bi-sectional method). Then, calculate differential pressure between point a and b (`dp1 = Branch_aAHUb.f2p(g)`). Then, calculate flow rate in `Branch_bAHP1a` is calculated based on `dp1` (`Branch_bAHP1a.p2f(-dp1)`).
The variable for the convergence judgement `g_eva` is the difference between flow in `Branch_aAHUb` and `Branch_bASHP1a`. If `g_eva` is greater than 0, reset `g_max`; otherwise, reset `g_min`.  
What the flow balance calculation does is;  
1. assumes the flow rate of one branch and calculate differential pressure of the branch  
2. calculates the flow rate of the other branches based on the differential pressure calculated in 1.  
3. performs a convergence calculation to see if the sum of flow rate calculated in 2. is equal to the flow rate assumed in 1.  
This methodology itself can be applied even when the piping network becomes complex.
```
        g_min = 0.0
        g_max = 0.5
        g_eva = 0.5
        cnt = 0
        while (g_eva > 0.001) or (g_eva < -0.001):
            cnt += 1
            g = (g_max + g_min) / 2
            dp1 = Branch_aAHUb.f2p(g)
            Branch_bAHP1a.p2f(-dp1)
            g_eva = Branch_aAHUb.g - Branch_bASHP1a.g
            if g_eva > 0:
                g_max = g
            else:
                g_min = g
            if cnt > 30:
                break
```
### temperature and power calculation  
`AHU_0` and `ASHP1_0` store the value of the equipment variable as the value of the previous time step. In this program, the inlet temperature of the equipment refers to the outlet temperature of the other equipment at the previous time step.
```
    AHU_0 = copy.deepcopy(AHU)
    ASHP1_0 = copy.deepcopy(AHP1)
    AHU.cal(g=Vlv_AHU.g, tin=ASHP1_0.tout_ch, q_load=q_load)
    ASHP1.cal(tout_ch_sv=t_supply_sv, tin_ch=AHU_0.tout, g_ch=CP1.g, tdb=tdb)
    CP1.cal()
```
Write calculation result to the dataframe
```
    output_data.iloc[calstep] = np.array([[g_load, AHU.g, AHU.tin, AHU.tout, Vlv_AHU.vlv, -Branch_aAHUb.dp, CP1.g, CP1.inv, CP1.pw, CP1.dp, CP1.ef,
                                           ASHP1.g_ch, ASHP1.tin_ch, ASHP1.tout_ch, ASHP1.cop, ASHP1.pw, ASHP1.pl, tdb]])
    
    current_time += datetime.timedelta(minutes=1)
```
### save the simulation result
```
output_data = output_data.resample('15min').mean()
output_data.to_csv('result_15min.csv')
```
