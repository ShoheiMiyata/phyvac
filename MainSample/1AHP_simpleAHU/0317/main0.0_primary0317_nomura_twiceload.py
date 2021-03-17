"""
@author: akrnmr
"""
# AHP1　   空冷ヒートポンプ
# CP1   　冷温水１次ポンプ
# AHU　   空調機

import pandas as pd
import time
import phyvac_primary_nomura as pv
from tqdm import tqdm
import copy
import numpy as np

start = time.time()

# 入力値の読み込み
input_data = pd.read_csv("Input15min_20180821_0824_twiceload.csv", index_col=0, parse_dates=True)
input_data = input_data.resample('1min').interpolate()
# 出力データフレームの作成
output_data = input_data.drop(input_data.columns[[0, 1, 2, 3, 4]], axis=1)
output_data = output_data.assign(AHU_g=0.0, AHU_tin=0.0, AHU_tout=0.0, g_load=0.0, CP1_g=0.0, CP1_inv=0.0, CP1_pw=0.0,
                                 CP1_dp=0.0, CP1_ef=0.0, AHP1_g_ch=0.0, AHP1_tin_ch=0.0, AHP1_tout_ch=0.0, AHP1_COP=0.0,
                                 AHP1_pw=0.0, AHP1_pl=0.0, tdb=0.0)

# 機器の定義
AHU = pv.AHU_simple(kr=1000)  # HEXのAHUであり、単位は[kPa/(m3/min)^2]だがkr=1000で、オーダー大丈夫？なおパイプのKr=500
Vlv_AHU = pv.Valve(cv_max=40, r=100)  # R元プログラムでは分からなかった
CP1 = pv.Pump(pg=[278.22, 37.32, -1543.39], eg=[0, 5.6657, -13.8139], r_ef=0.8)
AHP1 = pv.AirSourceHeatPump(tin_ch_d=12, tout_ch_d=7, g_ch_d=0.215, kr_ch=13.9, signal_hp=1)  # kr=7560, パイプのKr=6100

# 枝の定義
# Branch01  機器、バルブを有する枝
# Branch10  ポンプ・機器を有する枝
Branch_aAHUb = pv.Branch01(valve=Vlv_AHU, kr_eq=AHU.kr, kr_pipe=0.345)
Branch_bAHP1a = pv.Branch10(pump=CP1, kr_eq=AHP1.kr_ch, kr_pipe=25.52)

# 制御の定義
PID_AHU_Vlv = pv.PID(kp=0.3, ti=400)
PID_CP1 = pv.PID(kp=0.1, ti=500, a_min=0)
# 0.08, ti=500
# 0.05, ti=500
# 0.03, ti=500
# 0.01, ti=300
# 0.003, ti=300から上に上るように調節していった

for calstep in tqdm(range(24*60*4)):
    g_load = input_data.iat[calstep, 0]        # 負荷流量[m3/min]
    q_load = input_data.iat[calstep, 1]        # 負荷熱量[GJ/min]
    t_supply_sv = input_data.iat[calstep, 2]   # 供給水温設定値[℃]
    tdb = input_data.iat[calstep, 3]           # 外気乾球温度[℃]
    rh = input_data.iat[calstep, 4]            # 外気相対湿度[%](0~100)

    # 設定値演算
    AHP1.tout_ch_d = t_supply_sv

    # 制御
    # 昼間
    if (60*(24*0+9) <= calstep < 60*(24*0+18)) or (60*(24*1+9) <= calstep < 60*(24*1+18)) or \
            (60*(24*2+9) <= calstep < 60*(24*2+18)) or (60*(24*3+9) <= calstep < 60*(24*3+18)):  # 9:00~18:00に運転
        Vlv_AHU.vlv = PID_AHU_Vlv.control(sv=g_load, mv=Vlv_AHU.g)
        CP1.inv = PID_CP1.control(sv=g_load, mv=CP1.g)

        # 流量計算
        # 冷水系
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

        # 前時刻の温度を保存
        AHU_0 = copy.deepcopy(AHU)
        AHP1_0 = copy.deepcopy(AHP1)

        # 現時刻の温度・消費電力計算
        AHU.cal(g=Vlv_AHU.g, tin=AHP1_0.tout_ch, q_load=q_load)
        if (CP1.g > 0) and (AHU.g > 0):
            AHP1.cal(tin_ch=AHU_0.tout, g_ch=CP1.g, tdb=tdb, signal_hp=1)
            CP1.cal()

    # 夜間
    else:
        AHP1.tin_ch = 7
        Vlv_AHU.vlv = 0
        CP1.inv = 0
        # 前時刻の温度を保存
        AHU_0 = copy.deepcopy(AHU)
        AHP1_0 = copy.deepcopy(AHP1)

        # 現時刻の温度・消費電力計算
        AHU.cal(g=0, tin=AHP1_0.tout_ch, q_load=q_load)
        AHP1.cal(tin_ch=AHU_0.tout, g_ch=0, tdb=tdb, signal_hp=0)
        CP1.cal()

    output_data.iloc[calstep] = np.array([[AHU.g, AHU.tin, AHU.tout, g_load, CP1.g, CP1.inv, CP1.pw, CP1.dp, CP1.ef,
                                           AHP1.g_ch, AHP1.tin_ch, AHP1.tout_ch, AHP1.COP, AHP1.pw, AHP1.pl, tdb]])


output_data = output_data.resample('15min').mean()
output_data = output_data['2018-08-21 00:00': '2018-08-25 00:00']
output_data.to_csv('result2018_15min_twiceload2.csv')

print(time.time() - start)
