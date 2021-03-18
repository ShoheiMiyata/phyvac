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
import modules used in this program
~~~
import phyvac as pv
import pandas as pd
import time
import copy
import numpy as np
import datetime
~~~  
read input files
~~~
input_data = pd.read_csv("Input15min.csv", index_col=0, parse_dates=True)
input_data = input_data.resample('1min').interpolate()
~~~
create output dataframe
~~~
output_data = input_data.drop(input_data.columns[[0, 1, 2, 3, 4]], axis=1)
output_data = output_data.assign(g_load=0.0, AHU_g=0.0, AHU_tin=0.0, AHU_tout=0.0, AHU_vlv=0.0, dp_header=0.0, CP1_g=0.0, CP1_inv=0.0, CP1_pw=0.0,
                                 CP1_dp=0.0, CP1_ef=0.0, AHP1_g_ch=0.0, AHP1_tin_ch=0.0, AHP1_tout_ch=0.0, AHP1_COP=0.0,
                                 AHP1_pw=0.0, AHP1_pl=0.0, tdb=0.0)
~~~

define equipment
~~~
AHU = pv.AHU_simple(kr=1000)
Vlv_AHU = pv.Valve(cv_max=40, r=100)
CP1 = pv.Pump(pg=[108.22, 37.32, -1543.39], eg=[0, 5.6657, -13.8139], r_ef=0.8)
AHP1 = pv.AirSourceHeatPump(spec_table=pd.read_excel('equipment_spec.xlsx', sheet_name='AirSourceHeatPump',encoding="SHIFT-JIS",header=None))
~~~
define branch
~~~
Branch_aAHUb = pv.Branch01(valve=Vlv_AHU, kr_eq=AHU.kr, kr_pipe=1000)
Branch_bAHP1a = pv.Branch10(pump=CP1, kr_eq=AHP1.kr_ch, kr_pipe=1000)
~~~
define control
~~~
PID_AHU_Vlv = pv.PID(kp=0.3, ti=400)
PID_CP1 = pv.PID(kp=0.3, ti=500, a_min=0)
~~~
time step calculation: input boundary condition
~~~
current_time = datetime.datetime(2018, 9, 21, 0, 0)
for calstep in tqdm(range(24*60*4)):
    g_load = input_data.iat[calstep, 0]        # 負荷流量[m3/min]
    q_load = input_data.iat[calstep, 1]        # 負荷熱量[MJ/min]
    t_supply_sv = input_data.iat[calstep, 2]   # 供給水温設定値[℃]
    tdb = input_data.iat[calstep, 3]           # 外気乾球温度[℃]
    rh = input_data.iat[calstep, 4]            # 外気相対湿度[%](0~100)
~~~
control pump and valve
The system is operated from 9:00 to 18:00. The valve for AHU is controled according to the load flow and the pump is controled to keep the differential pressure between headers to the set value.
~~~
    if current_time.hour >= 9 and current_time.hour < 18: # daytime
        CP1.inv = PID_CP1.control(sv=50, mv=-Branch_aAHUb.dp)
        Vlv_AHU.vlv = PID_AHU_Vlv.control(sv=g_load, mv=Vlv_AHU.g)
    else: # nighttime
        CP1.inv = 0
        Vlv_AHU.vlv = 0
~~~
flow balance calculation  
~~~
        g_eva = 0.28
        g_max = 0.28  # ポンプの最大流量
        g_min = 0
        cnt = 0
        while (g_eva > 0.001) or (g_eva < -0.001):
            cnt += 1
            g = (g_max + g_min) / 2
            p1 = Branch_aAHUb.f2p(g)
            Branch_bAHP1a.p2f(-p1)
            g_eva = Branch_aAHUb.g - Branch_bAHP1a.g
            if g_eva > 0:
                g_max = g
            else:
                g_min = g
            if cnt > 30:
                break
~~~
temperature and power calculation  
Inlet temperature of equipment refers the outlet temperature at the previous time step.
~~~
    AHU_0 = copy.deepcopy(AHU)
    AHP1_0 = copy.deepcopy(AHP1)
    AHU.cal(g=Vlv_AHU.g, tin=AHP1_0.tout_ch, q_load=q_load)
    AHP1.cal(tout_ch_sv=t_supply_sv, tin_ch=AHU_0.tout, g_ch=CP1.g, tdb=tdb)
    CP1.cal()
~~~
Write calculation result to the dataframe and save it as an output file.
~~~
    output_data.iloc[calstep] = np.array([[g_load, AHU.g, AHU.tin, AHU.tout, Vlv_AHU.vlv, -Branch_aAHUb.dp, CP1.g, CP1.inv, CP1.pw, CP1.dp, CP1.ef,
                                           AHP1.g_ch, AHP1.tin_ch, AHP1.tout_ch, AHP1.cop, AHP1.pw, AHP1.pl, tdb]])
    
    current_time += datetime.timedelta(minutes=1)
    
output_data = output_data.resample('15min').mean()
output_data.to_csv('result_15min.csv')
~~~

## Main文の構成
main文は  
- 入力ファイルの読み込み
- 機器・枝・制御の定義
- 毎時刻計算
  - 外気温湿度や熱負荷などの境界条件の入力
  - 機器制御
  - 流量計算
  - 温度・消費電力計算
- 出力ファイルの保存  

という流れで構成されます。
