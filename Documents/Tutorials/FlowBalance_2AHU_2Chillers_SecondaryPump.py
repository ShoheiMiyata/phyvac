# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 13:03:00 2021

@author: shhmy
"""

import phyvac as pv

# 機器の定義
AHU1 = pv.AHU_simple(kr=2.0)
Vlv_AHU1 = pv.Valve(cv_max=800,r=100)
AHU2 = pv.AHU_simple(kr=2.0)
Vlv_AHU2 = pv.Valve(cv_max=800,r=100)
CP1 = pv.Pump(pg=[233.9,5.9578,-4.460], eg=[0.009964,0.4174,-0.0508])
CP2 = pv.Pump(pg=[233.9,5.9578,-4.460], eg=[0.009964,0.4174,-0.0508])
CP3 = pv.Pump(pg=[233.9,5.9578,-4.460], eg=[0.009964,0.4174,-0.0508])
Vlv_CP3 = pv.Valve(cv_max=800,r=100)
# 枝の定義
BranchaCP3b = pv.Branch11(valve=Vlv_CP3, pump=CP3, kr_pipe_pump=3.0, kr_pipe_valve=4.0)
Branch_bAHU1c = pv.Branch01(Vlv_AHU1, kr_eq=AHU1.kr, kr_pipe=3.0)
Branch_bAHU2c = pv.Branch01(Vlv_AHU2, kr_eq=AHU2.kr, kr_pipe=3.0)
Branch_cChiller1a = pv.Branch10(pump=CP1, kr_eq=10.0, kr_pipe=7.0)
Branch_cChiller2a = pv.Branch10(pump=CP2, kr_eq=10.0, kr_pipe=7.0)

# 弁開度、ポンプinvの入力
Vlv_AHU1.vlv = 0.6
Vlv_AHU2.vlv = 0.8
CP1.inv = 0.7
CP2.inv = 0.7
CP3.inv = 0.6
Vlv_CP3.vlv = 0.0

# 流量計算
g1_min = 0.0
g1_max = 20.0
g1_eva = 10.0
cnt1 = 0
while(g1_eva > 0.01)or(g1_eva < -0.01):
    cnt1 += 1
    g1 = (g1_max + g1_min) / 2
    dp1 = BranchaCP3b.f2p(g1)
    dp2_min = -300.0
    dp2_max = 0.0
    dp2_eva = 100.0
    cnt2 = 0
    while(dp2_eva > 0.01)or(dp2_eva < -0.01):
        cnt2 += 1
        dp2 = (dp2_max + dp2_min) / 2
        Branch_bAHU1c.p2f(dp2)
        Branch_bAHU2c.p2f(dp2)
        Branch_cChiller1a.p2f(-dp1-dp2)
        Branch_cChiller2a.p2f(-dp1-dp2)
        dp2_eva = Branch_bAHU1c.g + Branch_bAHU2c.g - Branch_cChiller1a.g - Branch_cChiller2a.g
        if dp2_eva > 0:
            dp2_min = dp2
        else:
            dp2_max = dp2
        if cnt2 > 30:
            break

    g1_eva = BranchaCP3b.g - Branch_cChiller1a.g - Branch_cChiller2a.g
    if g1_eva > 0:
        g1_max = g1
    else:
        g1_min = g1
    if cnt1 > 30:
        break
    
print(cnt1, cnt2, BranchaCP3b.g, Branch_bAHU1c.g, Branch_bAHU2c.g, Branch_cChiller1a.g, Branch_cChiller2a.g)