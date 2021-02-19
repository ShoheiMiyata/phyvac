"""
@author: akrnmr
"""
# RR1　   空冷ヒートポンプ
# CP1   　冷温水１次ポンプ
# AHU　   空調機

import pandas as pd
import time
import phyvac_nomura as pv
from tqdm import tqdm
import copy
import numpy as np

start = time.time()

# 入力値の読み込み
input_data = pd.read_csv("Input15min_20190707_0713_nomura.csv", index_col=0, parse_dates=True)  #　仙台TECのG_LdとQ_Ldを1/20にしたファイル
input_data = input_data.resample('1min').interpolate()
# 出力データフレームの作成
output_data = input_data.drop(input_data.columns[[0,1,2,3,4]], axis=1)
output_data = output_data.assign(AHU_g=0.0, AHU_tin=0.0, AHU_tout=0.0, CP1_g_sv=0.0, CP1_g=0.0, CP1_inv=0.0, CP1_pw=0.0,
                                 RR1_g=0.0, RR1_tin_ch=0.0, RR1_tout_ch=0.0, RR1_COP=0.0, RR1_pw=0.0, RR1_lf=0.0, t_da=0.0)

# 機器の定義
AHU = pv.AHU_simple(kr=2000)  # 元プログラムでは単位[kPa/(m3/min)^2]でkr=2000, オーダー大丈夫？
Vlv_AHU = pv.Valve(cv_max=40, r=100)  # R分からなかった
Vlv_Bypass = pv.Valve(cv_max=65, r=100)
CP1 = pv.Pump(pg=[278.22, 37.32, -1543.39], eg=[0, 5.6657, -13.8139], r_ef=0.58)
RR1 = pv.RR(tin_ch_d=12, tout_ch_d=7, g_ch_d=0.215, kr_ch=13.9, signal_hp=1)  # 外気温を時刻ごとの入力値とするには？

#枝の定義
#Branch00　機器のみを有する枝
#Branch01  機器、バルブを有する枝
#Branch10  ポンプ・機器を有する枝
#Branch11  並列ポンプ複数台とバイパス弁を有する枝
#Branch12  ポンプ、機器、バイパス弁を有する枝
Branch_aAHUb = pv.Branch01(valve=Vlv_AHU, kr_eq=AHU.kr, kr_pipe=0.345)
Branch_ab = pv.Branch01(valve=Vlv_Bypass, kr_eq=0, kr_pipe=12.76)
Branch_bRR1a = pv.Branch10(pump=CP1, kr_eq=RR1.kr_ch, kr_pipe=25.52)

# 制御の定義
PID_AHU_Vlv = pv.PID(kp=0.3, ti=400)
PID_Bypass_Vlv = pv.PID(kp=0.005, ti=500, a_min=0.3)
PID_CP1 = pv.PID(kp=0.003, ti=300, a_min=0.2)


for calstep in tqdm(range(24*60*14)):

    g_load = input_data.iat[calstep,0]        # 負荷流量[m3/min]
    q_load = input_data.iat[calstep,1]        # 負荷熱量[GJ/min]
    t_supply_sv = input_data.iat[calstep,2]   # 供給水温設定値[℃]
    t_da = input_data.iat[calstep,3]          # 外気乾球温度[℃]
    rh = input_data.iat[calstep,4]            # 外気相対湿度[%](0~100)

    # 設定値演算
    RR1.tout_ch_d = t_supply_sv

    # 制御
    Vlv_AHU.vlv = PID_AHU_Vlv.control(sv=g_load, mv=Vlv_AHU.g)
    Vlv_Bypass.vlv = 0.3  # 0.3で固定
    CP1_g_sv = g_load * 1.1  # 安全率10%的な意味か？
    CP1.inv = PID_CP1.control(sv=CP1_g_sv, mv=CP1.g)

    # 流量計算
    # 冷水系
    g_eva = 10
    g_max = 20
    g_min = 0
    cnt = 0
    while (g_eva > 0.01) or (g_eva < -0.01):
        cnt += 1
        g = (g_max + g_min) / 2
        p1 = Branch_aAHUb.f2p(g)
        Branch_ab.p2f(p1)
        Branch_bRR1a.p2f(-p1)
        g_eva = Branch_aAHUb.g + Branch_ab.g - Branch_bRR1a.g
        if g_eva > 0:
            g_max = g
        else:
            g_min = g
        if cnt > 30:
            break

    # 機器状態計算
    # 前時刻の温度を保存
    AHU_0 = copy.deepcopy(AHU)
    RR1_0 = copy.deepcopy(RR1)

    # 現時刻の温度・消費電力計算
    AHU.cal(g=Vlv_AHU.g, tin=RR1_0.tout_ch, q_load=q_load)
    if (CP1.g > 0) and (Vlv_Bypass.g + AHU.g > 0):
        tin_ch = (RR1_0.tout_ch * Vlv_Bypass.g + AHU_0.tout * AHU.g)/(Vlv_Bypass.g + AHU.g)
    RR1.cal(tin_ch=tin_ch, g_ch=CP1.g, t_da=t_da)
    CP1.cal()

    output_data.iloc[calstep] = np.array([[AHU.g, AHU.tin, AHU.tout, CP1_g_sv, CP1.g, CP1.inv, CP1.pw,
                                           RR1.g_ch, RR1.tin_ch, RR1.tout_ch, RR1.COP, RR1.pw, RR1.lf, t_da]])

output_data = output_data.resample('15min').mean()
output_data = output_data['2019-07-07 00:00': '2019-07-13 23:45']
output_data.to_csv('result2019_15min_nomura.csv')

print(time.time() - start)
