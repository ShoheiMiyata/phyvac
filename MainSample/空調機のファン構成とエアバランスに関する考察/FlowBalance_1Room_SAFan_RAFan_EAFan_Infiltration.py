# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 20:05:36 2021

@author: shhmy
"""

import phyvac as pv
import matplotlib.pyplot as plt
import numpy as np

# 機器の定義
Fan_SA = pv.Fan(pg=[100, -0.1, -0.1])
Fan_RA = pv.Fan(pg=[100, -0.1, -0.1])
Fan_EA = pv.Fan(pg=[100, -0.1, -0.1])

# 各ファン特性の描画
x = np.arange(0, 20, 0.1)
y = Fan_SA.pg[0] + Fan_SA.pg[1]*x + Fan_SA.pg[2]*x**2
plt.plot(x, y)
plt.title('Fan_SA P-Q curve')
plt.show()
x = np.arange(0, 20, 0.1)
y = Fan_RA.pg[0] + Fan_RA.pg[1]*x + Fan_RA.pg[2]*x**2
plt.plot(x, y)
plt.title('Fan_RA P-Q curve')
plt.show()
x = np.arange(0, 20, 0.1)
y = Fan_EA.pg[0] + Fan_EA.pg[1]*x + Fan_EA.pg[2]*x**2
plt.plot(x, y)
plt.title('Fan_EA P-Q curve')
plt.show()

# 枝の定義
Branch_ab = pv.Branch100(kr_duct=1.5)
Branch_bc = pv.Branch100(fan=Fan_SA,kr_duct=1.5)
Branch_gh = pv.Branch100(fan=Fan_EA,kr_duct=1.5)
Branch_de = pv.Branch100(fan=Fan_RA,kr_duct=1.5)
Branch_eb = pv.Branch100(kr_duct=1.5)
Branch_ef = pv.Branch100(kr_duct=1.5)
Branch_ij = pv.Branch100(kr_duct=1.5) # すき間

# ポンプinv, ダクト圧力損失係数の入力
Fan_SA.inv = 1.0
Fan_RA.inv = 0.6
Fan_EA.inv = 0.5
Branch_ab.kr_duct = 0.5
Branch_bc.kr_duct = 0.5
Branch_gh.kr_duct = 0.5
Branch_de.kr_duct = 0.5
Branch_eb.kr_duct = 0.5
Branch_ef.kr_duct = 0.5
Branch_ij.kr_duct = 0.5

# 流量計算
g_ab_min = 0.0
g_ab_max = 40.0
g_ab_eva = 20.0
cnt1 = 0
while(g_ab_eva > 0.001)or(g_ab_eva < -0.001):
    cnt1 += 1
    g_ab = (g_ab_max + g_ab_min) / 2
    dp_ab = Branch_ab.f2p(g_ab)
    
    g_eb_min = -40
    g_eb_max = 50
    g_eb_eva = 10
    cnt2 = 0
    while(g_eb_eva > 0.001)or(g_eb_eva < -0.001):
        cnt2 += 1
        g_eb = (g_eb_max + g_eb_min) / 2
        dp_eb = Branch_eb.f2p(g_eb)
        g_bc = g_ab + g_eb
        dp_bc = Branch_bc.f2p(g_bc)
        g_gh = Branch_gh.p2f(-dp_ab-dp_bc)
        g_ij = Branch_ij.p2f(-dp_ab-dp_bc)
        g_de = g_bc - g_gh - g_ij
        dp_de = Branch_de.f2p(g_de)
        g_eb2 = Branch_eb.p2f(-dp_bc-dp_de)
        g_eb_eva = g_eb - g_eb2
        if g_eb_eva > 0:
            g_eb_max = g_eb
        else:
            g_eb_min = g_eb
        
        if cnt2 > 30:
            break
    
    g_ef = g_de - g_eb
    dp_ef = Branch_ef.f2p(g_ef)
    g_ab2 = Branch_ab.p2f(-dp_ef-dp_de-dp_bc)
    g_ab_eva = g_ab - g_ab2   
    if g_ab_eva > 0:
        g_ab_max = g_ab
    else:
        g_ab_min = g_ab
    
    if cnt1 > 30:
        break
   
print("収束判定(30以下なら問題なし):", cnt1, cnt2)
print("室圧: ", round(dp_ab+dp_bc,3),"Pa")
print("各ダクトの風量(m3/min,矢印の向きが正)")
print("←", round(Branch_ef.g,2), "－－－",  round(Branch_de.g,2), "－",)
print("          ↓        ｜")
print("        ",round(Branch_eb.g,2), "     室 →EAファン:", round(Branch_gh.g,2))
print("          ｜          →すき間:", round(Branch_ij.g,2))
print("          ｜        ↑")
print("→",round(Branch_ab.g,2), "－－－", round(Branch_bc.g,2), "－",)





