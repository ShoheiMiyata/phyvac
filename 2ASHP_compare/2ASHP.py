"""
@author: akrnmr
"""
# AHP1　   空冷ヒートポンプ
# CP1   　冷温水１次ポンプ
# AHU　   空調機

import pandas as pd
import time
import phyvac as pv
from tqdm import tqdm
import copy
import numpy as np
import datetime

start = time.time()

# 入力値の読み込み
input_data = pd.read_csv("/Users/koguretomota/phyvac/2ASHP_compare/Input15min_2ASHP_simpleAHU.csv", index_col=0, parse_dates=True)
input_data = input_data.resample('1min').interpolate()
# 出力データフレームの作成
output_data = input_data.drop(input_data.columns[[0, 1, 2, 3, 4]], axis=1)
output_data = output_data.assign(g_load=0.0, AHU_g=0.0, AHU_tin=0.0, AHU_tout=0.0, AHU_vlv=0.0, dp_header=0.0, CP1_g=0.0, CP1_inv=0.0, CP1_pw=0.0,
                                 CP1_dp=0.0, CP1_ef=0.0, CP2_g=0.0, CP2_inv=0.0, CP2_pw=0.0, CP2_dp=0.0, CP2_ef=0.0, AHP1_g_ch=0.0, AHP1_tin_ch=0.0,
                                 AHP1_tout_ch=0.0, AHP1_COP=0.0, AHP1_pw=0.0, AHP1_pl=0.0, AHP2_g_ch=0.0, AHP2_tin_ch=0.0, AHP2_tout_ch=0.0, AHP2_COP=0.0,
                                 AHP2_pw=0.0, AHP2_pl=0.0 ,tdb=0.0, num=0.0)

# 機器の定義
AHU = pv.AHU_simple(kr=1000)  # HEXのAHUであり、単位は[kPa/(m3/min)^2]だがkr=1000で、オーダー大丈夫？なおパイプのKr=500
Vlv_AHU = pv.Valve(cv_max=40, r=100)
CP1 = pv.Pump(pg=[108.22, 0, -1543.39], eg=[0, 5.6657, -13.8139], r_ef=0.8)
CP2 = pv.Pump(pg=[108.22, 0, -1543.39], eg=[0, 5.6657, -13.8139], r_ef=0.8)
AHP1 = pv.AirSourceHeatPump(spec_table=pd.read_excel('equipment_spec.xlsx', sheet_name='AirSourceHeatPump',header=None))
AHP2 = pv.AirSourceHeatPump(spec_table=pd.read_excel('equipment_spec.xlsx', sheet_name='AirSourceHeatPump',header=None))

# 枝の定義
# Branch01  機器、バルブを有する枝
# Branch10  ポンプ・機器を有する枝
Branch_aAHUb = pv.Branch01(valve=Vlv_AHU, kr_eq=AHU.kr, kr_pipe=1000)
Branch_bAHP1a = pv.Branch10(pump=CP1, kr_eq=AHP1.kr_ch, kr_pipe=1000)
Branch_bAHP2a = pv.Branch10(pump=CP2, kr_eq=AHP2.kr_ch, kr_pipe=1000)


# 制御の定義
PID_AHU_Vlv = pv.PID(kp=0.03, ti=40)
PID_CP1 = pv.PID(kp=0.03, ti=50, a_min=0)
PID_CP2 = pv.PID(kp=0.03, ti=50, a_min=0)
UnitnumASHP = pv.UnitNum(thre_up=[0.09], thre_down=[0.12], t_wait=30)


current_time = datetime.datetime(2018, 9, 21, 0, 0)
for calstep in tqdm(range(24*60*4)):

    g_load = input_data.iat[calstep, 0]        # 負荷流量[m3/min]
    q_load = input_data.iat[calstep, 1]        # 負荷熱量[MJ/min]
    t_supply_sv = input_data.iat[calstep, 2]   # 供給水温設定値[℃]
    tdb = input_data.iat[calstep, 3]           # 外気乾球温度[℃]
    rh = input_data.iat[calstep, 4]            # 外気相対湿度[%](0~100)

    # 設定値演算
    AHP1.tout_ch_d = t_supply_sv
    AHP2.tout_ch_d = t_supply_sv

    # 制御
    num = UnitnumASHP.control(g = g_load)

    # 昼間
    if current_time.hour >= 9 and current_time.hour < 18:  # 9:00~18:00に運転

        Vlv_AHU.vlv = PID_AHU_Vlv.control(sv=g_load, mv=Vlv_AHU.g)
        CP1.inv = PID_CP1.control(sv=120, mv=-Branch_aAHUb.dp) # ポンプはヘッダ間差圧を参照して制御
        if num == 1:
            CP2.inv = 0
        else:
            CP2.inv = PID_CP2.control(sv=120, mv=-Branch_aAHUb.dp)

        # 流量計算
        # 冷水系
        g_eva = 0.28
        g_max = 0.28  # ポンプの最大流量
        g_min = 0
        cnt = 0
        while (g_eva > 0.000001) or (g_eva < -0.000001):
            cnt += 1
            g = (g_max + g_min) / 2
            p1 = Branch_aAHUb.f2p(g)

            Branch_bAHP1a.p2f(-p1)
            Branch_bAHP2a.p2f(-p1)
            g_eva = Branch_aAHUb.g - Branch_bAHP1a.g - Branch_bAHP2a.g

            if g_eva > 0:
                g_max = g
            else:
                g_min = g
            if cnt > 30:
                break
        #print(current_time,num,Branch_aAHUb.g,CP1.g,Branch_bAHP1a.g,CP2.g,Branch_bAHP2a.g)
        #print(current_time, Branch_bAHP1a.dp, CP1.dp, CP2.dp, CP1.inv, CP2.inv, g_load, g, cnt)

        #台数制御をここに入れる
        
    # 夜間
    else:
        Vlv_AHU.vlv = 0
        CP1.inv = 0
        CP2.inv = 0
        
        Branch_aAHUb.f2p(0)
        AHU.g = 0
        AHP1.g = 0
        AHP2.g = 0
        CP1.g = 0
        CP2.g = 0

        Branch_bAHP1a.p2f(0)
        Branch_bAHP2a.p2f(0)

        CP1.dp = 0
        CP2.dp = 0


    # 前時刻の温度を保存
    AHU_0 = copy.deepcopy(AHU)
    AHP1_0 = copy.deepcopy(AHP1)
    AHP2_0 = copy.deepcopy(AHP2)

    # 現時刻の温度・消費電力計算
    AHU.cal(g=Vlv_AHU.g, tin=AHP1_0.tout_ch, q_load=q_load)
    AHP1.cal(tout_ch_sv=t_supply_sv, tin_ch=AHU_0.tout, g_ch=CP1.g, tdb=tdb)
    AHP2.cal(tout_ch_sv=t_supply_sv, tin_ch=AHU_0.tout, g_ch=CP2.g, tdb=tdb)
    CP1.cal()
    CP2.cal()

    output_data.iloc[calstep] = np.array([[g_load, AHU.g, AHU.tin, AHU.tout, Vlv_AHU.vlv, -Branch_aAHUb.dp, CP1.g, CP1.inv, CP1.pw, CP1.dp, CP1.ef, CP2.g, CP2.inv, CP2.pw, CP2.dp, CP2.ef,
                                           AHP1.g_ch, AHP1.tin_ch, AHP1.tout_ch, AHP1.cop, AHP1.pw, AHP1.pl, AHP2.g_ch, AHP2.tin_ch, AHP2.tout_ch, AHP2.cop, AHP2.pw, AHP2.pl, tdb, num]])
    
    current_time += datetime.timedelta(minutes=1)
    
output_data = output_data.resample('15min').mean()
output_data = output_data['2018-08-21 00:00': '2018-08-25 00:00']
output_data.to_csv('result_15min120.csv')

print(time.time() - start)