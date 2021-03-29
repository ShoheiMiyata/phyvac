# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 08:52:36 2021

@author: shhmy
"""


import phyvac as pv

# 機器の定義
AHU1 = pv.AHU_simple(kr=2.0)
Vlv_AHU = pv.Valve(cv_max=800,r=100)
CP1 = pv.Pump(pg=[233.9,5.9578,-4.460], eg=[0.009964,0.4174,-0.0508])
CP2 = pv.Pump(pg=[233.9,5.9578,-4.460], eg=[0.009964,0.4174,-0.0508])
CP3 = pv.Pump(pg=[233.9,5.9578,-4.460], eg=[0.009964,0.4174,-0.0508])
# 枝の定義
Branch_aAHUb = pv.Branch01(Vlv_AHU, kr_eq=AHU1.kr, kr_pipe=3.0)
Branch_bChiller1a = pv.Branch10(pump=CP1, kr_eq=10.0, kr_pipe=7.0)
Branch_bChiller2a = pv.Branch10(pump=CP2, kr_eq=10.0, kr_pipe=7.0)
Branch_bChiller3a = pv.Branch10(pump=CP3, kr_eq=10.0, kr_pipe=7.0)


# 弁開度、ポンプinvの入力
Vlv_AHU.vlv = 0.8
CP1.inv = 0.8
CP2.inv = 0.7
CP3.inv = 0.6

# 流量計算
g_min = 0.0
g_max = 20.0
g_eva = 10.-0
cnt = 0
while(g_eva > 0.01)or(g_eva < -0.01):
    cnt += 1
    g = (g_max + g_min) / 2
    dp1 = Branch_aAHUb.f2p(g)
    Branch_bChiller1a.p2f(-dp1)
    Branch_bChiller2a.p2f(-dp1)
    Branch_bChiller3a.p2f(-dp1)
    g_eva = Branch_aAHUb.g - Branch_bChiller1a.g - Branch_bChiller2a.g - Branch_bChiller3a.g
    if g_eva > 0:
        g_max = g
    else:
        g_min = g
    if cnt > 30:
        break
    
print(cnt, Branch_aAHUb.g, Branch_bChiller1a.g, Branch_bChiller2a.g, Branch_bChiller3a.g)