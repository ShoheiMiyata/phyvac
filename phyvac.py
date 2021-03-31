# -*- coding: utf-8 -*-
"""
@author: shhmy
"""
# phyvacモジュール。hvav + python ->phyvac
# 空調システムの計算を極力物理原理・詳細な制御ロジックに基づいて行う。現在は熱源システムが中心（2021.01.21）
# ver0.1 20210128
# branch_miyataテスト

import numpy as np
import math
import pandas as pd
from scipy.interpolate import RegularGridInterpolator
from scipy import optimize

# 空気状態関数　###############################################################
# 空気調和・衛生工学会編：空気調和・衛生工学便覧14版，1基礎編，第3章, pp.39-56，2010.
# 式の読み方↓
# tdb_w2h   [input]tdb(dry-bulb temperature), w(absolute humidity) -> [output] h(enthalpy)

# twb       湿球温度['C]
# tdb       乾球温度['C]
# tdp       露点温度['C]
# w         絶対湿度[kg/kg']
# pv        水蒸気分圧[kPa]            vapor pressure
# psat      飽和空気の水蒸気分圧[kPa]    saturated vapor pressure
# h         比エンタルピー[kJ/kg']
# rh        相対湿度[%]
# den       密度[kg/m^3]              density
# p_atm     標準大気圧[kPa]


CA = 1.006  # 乾き空気の定圧比熱 [kJ/kg・K]
CV = 1.86  # 水蒸気の定圧比熱 [kJ/kg・K]
R0 = 2.501 * 10 ** 3  # 0'Cの水の蒸発潜熱 [kJ/kg]


# 乾球温度と相対湿度から露点温度['C]
def tdb_rh2tdp(tdb, rh):
    # 飽和水蒸気圧psat[mmHg]の計算
    c = 373.16 / (273.16 + tdb)
    b = c - 1
    a = -7.90298 * b + 5.02808 * math.log10(c) - 1.3816 * 10 ** (-7) * (10 ** (11.344 * b / c) - 1) + 8.1328 * 10 ** (
        -3) * (10 ** (-3.49149 * b) - 1)
    psat = 760 * 10 ** a
    # 入力した絶対湿度
    x = 0.622 * (rh * psat) / 100 / (760 - rh * psat / 100)

    # この絶対湿度で相対湿度100%となる飽和水蒸気圧psat
    psat = 100 * 760 * x / (100 * (0.622 + x))
    psat0 = 0
    tdp_max = tdb
    tdp_min = -20
    tdp = 0
    cnt = 0
    # 飽和水蒸気圧が上のpsatの値となる温度twb
    while (psat - psat0 < -0.01) or (psat - psat0 > 0.01):

        tdp = (tdp_max + tdp_min) / 2

        c = 373.16 / (273.16 + tdp)
        b = c - 1
        a = -7.90298 * b + 5.02808 * math.log10(c) - 1.3816 * 10 ** (-7) * (
                    10 ** (11.344 * b / c) - 1) + 8.1328 * 10 ** (-3) * (10 ** (-3.49149 * b) - 1)
        psat0 = 760 * 10 ** a

        if psat - psat0 > 0:
            tdp_min = tdp
        else:
            tdp_max = tdp

        cnt += 1
        if cnt > 30:
            break

    return tdp


# 乾球温度tdbと相対湿度rhから比エンタルピーh[kJ/kg']と絶対湿度x[kg/kg']
def tdb_rh2h_x(tdb, rh):
    # 飽和水蒸気圧Ps[mmHg]の計算
    c = 373.16 / (273.16 + tdb)
    b = c - 1
    a = -7.90298 * b + 5.02808 * math.log10(c) - 1.3816 * 10 ** (-7) * (10 ** (11.344 * b / c) - 1) + 8.1328 * 10 ** (
        -3) * (10 ** (-3.49149 * b) - 1)
    psat = 760 * 10 ** a
    w = 0.622 * (rh * psat) / 100 / (760 - rh * psat / 100)
    h = CA * tdb + (R0 + CV * tdb) * w

    return [h, w]


# 乾球温度から飽和水蒸気圧[kPa]
def tdb2psat(tdb):
    # Wagner equation
    x = (1 - (tdb + 273.15) / 647.3)
    psat = 221200 * math.exp((-7.76451 * x + 1.45838 * x ** 1.5 + -2.7758 * x ** 3 - 1.23303 * x ** 6) / (1-x))  # [hPa]
    return psat / 10  # [hPa] -> [kPa]


# 乾球温度と相対湿度から湿球温度['C]
def tdb_rh2twb(tdb, rh):
    psat = tdb2psat(tdb)
    pv_1 = rh / 100 * psat
    pv_2 = -99999
    twb = 0
    twb_max = 50
    twb_min = -50
    cnt = 0
    while abs(pv_1 - pv_2) > 0.01:
        twb = (twb_max + twb_min) / 2
        # Sprung equation
        pv_2 = tdb2psat(twb) - 0.000662 * 1013.25 * (tdb - twb)

        if pv_1 - pv_2 > 0:
            twb_min = twb
        else:
            twb_max = twb

        cnt += 1
        if cnt > 20:
            break

    return twb

 
# # 湿球温度の算出
# def wet_bulb_temperature(Tda, rh):
#     # cpw   :水比熱[J/kg'C]
#     cpw = 4184
    
#     Tdp = dew_point_temperature(Tda,rh)
#     # print(Tdp)

#     Twbmax = Tda
#     Twbmin = Tdp
#     Twb = 1
#     Twb0 = 0
#     cnt = 0
#     while(Twb - Twb0 > 0.01)or(Twb - Twb0 < - 0.01):
    
#         Twb = (Twbmax + Twbmin) / 2
#         [h,x] = tdb_rh2h_x(Tda,rh)
#         [hs,xs] = tdb_rh2h_x(Twb,100)
#         Twb0 = (hs - h) / ((xs - x) * cpw)
        
#         if Twb - Twb0 > 0:
#             Twbmin = Twb
#         else:
#             Twbmax = Twb
          
#         cnt += 1
#         if cnt > 30:
#             break
    
#     return Twb



# 乾球温度と絶対湿度から比エンタルピー[kJ/kg']
def tdb_w2h(tdb, w):
    return CA * tdb + (CV * tdb + R0) * w


# 乾球温度から飽和水蒸気圧の比エンタルピー[kJ/kg']
def tdb2hsat(tdb):
    psat = tdp2psat(tdb)
    wsat = pv2w(psat)
    hsat = tdb_w2h(tdb, wsat)
    return hsat


# 絶対湿度から蒸気圧[kPa]
def w2pv(w, p_atm=101.325):
    return p_atm * w / (0.622 + w)


# 蒸気圧から絶対湿度['C]
def pv2w(pv, p_atm=101.325):
    w = 0.622 * pv / (p_atm - pv)
    return w


# 露点温度から飽和水蒸気圧[単位不明、おそらくkPaだが…]
def tdp2psat(tdp):
    p_convert = 0.001

    c1 = -5.6745359e3
    c2 = 6.3925247
    c3 = -9.6778430e-3
    c4 = 6.2215701e-7
    c5 = 2.0747825e-9
    c6 = -9.4840240e-13
    c7 = 4.1635019

    n1 = 0.11670521452767e4
    n2 = -0.72421316703206e6
    n3 = -0.17073846940092e2
    n4 = 0.12020824702470e5
    n5 = -0.32325550322333e7
    n6 = 0.14915108613530e2
    n7 = -0.4823265731591e4
    n8 = 0.40511340542057e6
    n9 = -0.23855557567849e0
    n10 = 0.65017534844798e3

    t = tdp + 273.15
    if tdp < 0.01:
        psat = math.exp(c1 / t + c2 + c3 * t + c4 * t ** 2 + c5 * t ** 3 + c6 * t ** 4 + c7 * math.log(t)) * p_convert

    else:
        alpha = t + n9 / (t - n10)
        a2 = alpha ** 2
        a = a2 + n1 * alpha + n2
        b = n3 * a2 + n4 * alpha + n5
        c = n6 * a2 + n7 * alpha + n8
        psat = pow(2 * c / (-b + pow(b ** 2 - 4 * a * c, 0.5)), 4) / p_convert

    return psat


# 比エンタルピーと相対湿度から絶対湿度[kg/kg']
def h_rh2w(h, rh):
    tdb = h_rh2tdb(h, rh)
    w = tdb_rh2w(tdb, rh)
    return w


# 乾球温度から密度[kg/m^3]
def tdb2den(tdb):
    return 1.293 * 273.3 / (273.2 + tdb)


# 比エンタルピーと相対湿度から乾球温度['C]
def h_rh2tdb(h, rh):
    def h_rh2tdb_fun(tdb):
        return h - tdb_rh2h(tdb, rh)
    return optimize.newton(h_rh2tdb_fun, x0=1e-5, tol=1e-4, maxiter=20)


# 乾球温度と相対湿度から比エンタルピー[kJ/kg']
def tdb_rh2h(tdb, rh):
    w = tdb_rh2w(tdb, rh)
    h = tdb_w2h(tdb, w)
    return h


# 乾球温度と相対湿度から絶対湿度[kg/kg']
def tdb_rh2w(tdb, rh):
    psat = tdp2psat(tdb)
    pv = 0.01 * rh * psat
    w = pv2w(pv)
    return w


# 飽和水蒸気圧から露点温度['C]
def psat2tdp(psat):
    p_convert = 0.001

    d1 = -6.0662e1
    d2 = 7.4624
    d3 = 2.0594e-1
    d4 = 1.6321e-2

    n1 = 0.11670521452767e4
    n2 = -0.72421316703206e6
    n3 = -0.17073846940092e2
    n4 = 0.12020824702470e5
    n5 = -0.32325550322333e7
    n6 = 0.14915108613530e2
    n7 = -0.4823265731591e4
    n8 = 0.40511340542057e6
    n9 = -0.23855557567849e0
    n10 = 0.65017534844798e3

    if psat < 0.611213:
        y = math.log(psat / p_convert)
        tdp = d1 + y * (d2 + y * (d3 + y * d4))
    else:
        ps = psat * p_convert
        beta = pow(ps, 0.25)
        b2 = beta ** 2
        e = b2 + n3 * beta + n6
        f = n1 * b2 + n4 * beta + n7
        g = n2 * b2 + n5 * beta + n8
        d = 2 * g / (-f - pow(f ** 2 - 4 * e * g, 0.5))
        tdp = (n10 + d - pow((n10 + d) ** 2 - 4 * (n9 + n10 * d), 0.5)) / 2 - 273.15
    return tdp


# 絶対湿度と比エンタルピーから乾球温度['C]
def w_h2tdb(w, h):
    tdb = (h - 2501 * w) / (1.006 + 1.86 * w)
    return tdb


# 絶対湿度と相対湿度から乾球温度['C]
def w_rh2tdb(w, rh):
    psat = w2pv(w)
    tdb = psat2tdp(psat / rh * 100)
    return tdb


# 絶対湿度から水蒸気の定圧比熱[kJ/kg･K] (= CA + CV)
def w2cpair(w):
    cpair = 1.006 + 1.86 * w
    return cpair


# 絶対湿度と乾球温度から相対湿度['C]
def w_tdb2rh(w, tdb):
    pv = w2pv(w)
    psat = tdp2psat(tdb)
    if psat <= 0:
        return 0
    else:
        return pv / psat * 100


# 乾球温度と湿球湿度から絶対湿度[kg/kg']
def tdb_twb2w(tdb, twb):
    psat = tdp2psat(twb)
    wsat = pv2w(psat)
    a = wsat * (2501 + (1.86 - 4.186) * twb) + 1.006 * (twb - tdb)  # 4.186[kJ/kg･K] 水の比熱
    b = 2501 + 1.86 * tdb - 4.186 * twb
    return a / b


#######################
# HEX function
# 宇田川光弘：パソコンによる空気調和計算法，オーム社，p.8-219，1986 年.
#######################
# 熱交換器の計算に必要なパラメータを取得する
def getparameter_hex(tdb):
    delta = 0.001
    hws1 = tdb2hsat(tdb)
    hws2 = tdb2hsat(tdb + delta)
    fa = (hws2 - hws1) / delta
    fb = hws1 - fa * tdb
    return fa, fb


# 熱通過有効度[-]を求める
def hex_effectiveness(ntu, ratio_heat_cap, flowtype):
    # flowtype : {'counterflow', 'parallelflow'}
    ratio = ratio_heat_cap

    if ratio <= 0:
        return 1 - math.exp(-ntu)
    if ntu == 0:
        return 0
    if flowtype == 'counterflow':
        if ratio < 1:
            return (1 - math.exp((ratio - 1) * ntu)) / (1 - ratio * math.exp((ratio - 1) * ntu))
        else:
            return ntu / (1 + ntu)
    elif flowtype == 'parallelflow':
        if ratio < 1:
            return (1 - math.exp(-ntu * (ratio + 1))) / (1 + ratio)
        else:
            return 0.5 * (1 - math.exp(-2 * ntu))
    else:
        print('error:flowtype')


# NTU(熱通過数:Number of transfer unit[-])を求める
def hex_ntu(feff, fratio_heat_cap, fflowtype):
    # flowtype : {'counterflow', 'parallelflow'}
    hex_eff = feff
    hex_ratio = fratio_heat_cap
    hex_flowtype = fflowtype

    def hex_efunc(fntu):
        return hex_eff - hex_effectiveness(fntu, hex_ratio, hex_flowtype)

    return optimize.newton(hex_efunc, x0=0, tol=1e-6, maxiter=20)  # rtol=1e-6 fprime=1e-4,




# 機器関係モデル ###############################################################

# バルブ特性
class Valve:
    def __init__(self, cv_max=800, r=100):
        # cv_max    :流量係数。
        # r         :レンジアビリティ。最も弁を閉じたときの流量比の逆数
        # vlv       :バルブ開度(1:全開,0:全閉)
        # dp        :バルブによる圧力損失[kPa]
        # g         ：流量 単位要確認!!
        self.cv_max = cv_max
        self.r = r
        self.dp = 0.0
        self.vlv = 0.0
        self.g = 0.0
        
    def f2p(self, g): # flow to pressure
        self.g = g
        # cv = self.cv_max * self.r**(self.vlv - 1)
        # self.dp = - 1743 * (self.g * 1000 / 60)**2 / cv**2 イコールパーセント特性
        if self.vlv == 0.0:
            self.dp = -99999999
        elif (self.cv_max * self.r**(self.vlv - 1))**2 > 0:
            self.dp = (- 1743 * (1000 / 60)**2 / (self.cv_max * self.r**(self.vlv - 1))**2) * self.g**2
        else:
            self.dp = 0.0
            
        return self.dp
    
    def p2f(self,dp):
        self.dp = dp
        if self.vlv == 0.0:
            self.g = 0
        elif self.dp < 0:
            self.g = (self.dp/((- 1743 * (1000 / 60)**2 / (self.cv_max * self.r**(self.vlv - 1))**2)))**0.5
        else:
            self.g = - (self.dp/((1743 * (1000 / 60)**2 / (self.cv_max * self.r**(self.vlv - 1))**2)))**0.5 # 逆流
        
        return self.g
    
    def f2p_co(self): # coefficient for f2p
        if self.vlv == 0.0:
            return np.array([0,0,-99999999])
        else:
            return np.array([0,0,(- 1743 * (1000 / 60)**2 / (self.cv_max * self.r**(self.vlv - 1))**2)])
        

# ポンプ特性と消費電力計算
class Pump:
    # 定格値の入力
    def __init__(self, pg=[233,5.9578,-4.95], eg=[0.0099,0.4174,-0.0508], r_ef=0.8):
        # pq    :圧力-流量(pg)曲線の係数（切片、一次、二次）
        # eq    :効率-流量(eg)曲線の係数（切片、一次、二次）
        # r_ef  :定格時の最高効率(本来は計算によって求める？)rated efficiency
        # inv   :回転数比(0.0~1.0)
        # dp_p  :ポンプ揚程[kPa]
        # g_p   :流量[m3/min]
        # pw_p  :消費電力[kW]
        # flag   :計算に問題があったら1、なかったら0
        # ef    :効率(0.0~1.0)
        self.pg = pg
        self.eg = eg
        self.r_ef = r_ef
        self.inv = 0.0
        self.dp = 0.0
        self.g = 0.0
        self.ef = 0.0
        self.pw = 0.0
        self.flag = 0
        self.num = 1
    
    def f2p(self, g): # flow to pressure for pump
        self.g = g
        # 流量がある場合のみ揚程を計算する
        if self.g > 0 and self.inv > 0:
            self.dp = (self.pg[0] + self.pg[1] *  (self.g / self.inv) + self.pg[2] *  (self.g / self.inv)**2) * self.inv**2
        else:
            self.dp = 0.0
            
        if self.dp < 0:
            self.dp = 0.0
            self.flag = 1
        else:
            self.flag = 0
            
        return self.dp
    
    def f2p_co(self): # coefficient for f2p
        return [self.pg[0]* self.inv**2, self.pg[1]*self.inv, self.pg[2]]
    
    
    def cal(self):
        # 流量がある場合のみ消費電力を計算する
        if self.g > 0 and self.inv > 0:
        
            # G: INV=1.0時（定格）の流量
            G = self.g / self.inv
            # K: 効率換算係数
            K = 1.0 - (1.0 - self.r_ef) / (self.inv**0.2) / self.r_ef 
            # ef: 効率
            self.ef = K * (self.eg[0] + self.eg[1] * G + self.eg[2] * G**2)
            
            self.dp = (self.pg[0] + self.pg[1] *  (self.g / self.inv) + self.pg[2] *  (self.g / self.inv)**2) * self.inv**2
            if self.dp < 0:
                self.dp = 0.0
                self.flag = 1
            # print(Nm)
        
            #  軸動力を求める
            if self.ef > 0:
                self.pw = 1.0 * self.g * self.dp / (60 * self.ef)
                self.flag = 0
            else:
                self.pw = 0.0
                self.flag = 2
            # print(self.flag)
        
        else:
            self.pw = 0.0
            self.ef = 0.0
            self.flag = 0
        
        
# 負荷率-COP曲線に基づく冷凍機COP計算。表は左から右、上から下に負荷率や冷却水入口温度が上昇しなければならない。
class Chiller:
    # 定格値の入力
    def __init__(self, spec_table=pd.read_excel('equipment_spec.xlsx', sheet_name='Chiller', header=None)):
        # tin   :入口温度[℃]
        # tout  :出口温度[℃]
        # g     :流量[m3/min]
        # q     :熱量[kW]
        # ch    :冷水（chilled water）
        # cd    :冷却水(condenser water)
        # d     :定格値
        # pw    :消費電力[kW]  
        # pl    :部分負荷率(load factor, 0.0~1.0)
        # kr_ch :蒸発器圧力損失係数[kPa/(m3/min)**2]
        # kr_cd :凝縮器圧力損失係数[kPa/(m3/min)**2]
        # dp    :機器による圧力損失[kPa]
        self.tout_ch_d = float(spec_table.iat[1,0])
        self.tin_ch_d = float(spec_table.iat[1,1])
        self.g_ch_d = float(spec_table.iat[1,2])
        self.tin_cd_d = float(spec_table.iat[1,3])
        self.tout_cd_d = float(spec_table.iat[1,4])
        self.g_cd_d = float(spec_table.iat[1,5])
        # 定格冷凍容量[kW]
        self.q_ch_d = (self.tin_ch_d - self.tout_ch_d)*self.g_ch_d*1000*4.186/60
        # 定格主電動機入力[kW]
        self.pw_d = float(spec_table.iat[1,6])
        self.kr_ch = float(spec_table.iat[1,7])
        self.kr_cd = float(spec_table.iat[1,8])
        # 補機電力[kW]
        self.pw_sub = 0
        # 定格冷凍機COP
        self.COP_rp = self.q_ch_d / self.pw_d
        # 以下、毎時刻変わる可能性のある値
        self.tout_ch = 7
        self.tout_cd = 37
        self.pw = 0
        self.q_ch = 0
        self.lf = 0 # 負荷率(0.0~1.0)
        self.cop = 0
        self.flag = 0 #問題があったら1,なかったら0
        self.dp_ch = 0
        self.dp_cd = 0
        self.tin_cd = 15
        self.tin_ch = 7
        
        pl_cop = spec_table.drop(spec_table.index[[0, 1, 2]])
        pl_cop.iat[0,0] = '-'
        pl_cop = pl_cop.dropna(how='all', axis=1)
        self.data = pl_cop.values

        
    # 機器特性表に基づく冷凍機COPの算出
    def cal(self,tout_ch_sv, tin_ch, g_ch, tin_cd, g_cd):
        self.flag = 0
        self.tout_ch_sv = tout_ch_sv
        self.tin_ch = tin_ch
        self.g_ch = g_ch
        self.tin_cd = tin_cd
        self.g_cd = g_cd
        # 冷水出口温度[℃]
        self.tout_ch = self.tout_ch_sv
        # 冷凍熱量[kW]
        self.q_ch = (self.tin_ch - self.tout_ch)*self.g_ch*1000*4.186/60

        if self.q_ch > 0 and self.g_cd > 0:
             
            pl = self.data[0][1:].astype(np.float32)
            temp = self.data.transpose()[0][1:].astype(np.float32)
            dataset = self.data[1:].transpose()[1:].transpose().astype(np.float32)
            cop = RegularGridInterpolator((temp, pl), dataset)
            
            # 部分負荷率
            self.pl = self.q_ch / self.q_ch_d
            pl_cop = self.pl
            if self.pl > pl[-1]:
                self.pl = pl[-1]
                pl_cop = self.pl
                self.tout_ch += (self.q_ch - self.q_ch_d)/(self.g_ch*1000*4.186/60)
                self.q_ch = self.q_ch_d
                self.flag = 1

            elif self.pl < pl[0]:
                pl_cop = pl[-1]
                self.flag = 2
            
            tin_cd_cop = self.tin_cd-(self.tout_ch-self.tout_ch_d)
            
            if tin_cd_cop < temp[0]:
                tin_cd_cop = temp[0]
                self.flag = 3
            elif tin_cd_cop > temp[-1]:
                tin_cd_cop = temp[-1]
                self.flag = 4

            self.cop = float(cop([[tin_cd_cop, pl_cop]]))
            self.pw = self.q_ch / self.cop + self.pw_sub
            self.tout_cd = (self.q_ch + self.pw)/(4.186*self.g_cd*1000/60) + self.tin_cd
            
            
        elif self.q_ch == 0:
            self.pw = 0
            self.cop = 0
            self.pl = 0
            # self.tout_cd = self.tin_cd
            self.flag = 0
        else:
            self.pw = 0
            self.cop = 0
            self.pl = 0
            # self.tout_cd = self.tin_cd
            self.flag = 5
        
        self.dp_ch = -self.kr_ch*g_ch**2
        self.dp_cd = -self.kr_cd*g_cd**2
    

# 負荷率-COP曲線に基づく空冷HPのCOP計算。表は左から右、上から下に負荷率や冷却水入口温度が上昇しなければならない。
# https://salamann.com/python-multi-dimension-data-interpolation
class AirSourceHeatPump:
    # 定格値の入力
    def __init__(self, spec_table=pd.read_excel('equipment_spec.xlsx', sheet_name='AirSourceHeatPump', header=None)):
        # tin   :入口温度[℃]
        # tout  :出口温度[℃]
        # g     :流量[m3/min]
        # q     :熱量[kW]
        # ch    :冷水（chilled water）
        # d     :定格値
        # pw    :消費電力[kW]  
        # pl    :部分負荷率(load factor, 0.0~1.0)
        # kr_ch :冷水圧力損失係数[kPa/(m3/min)**2]
        # dp    :機器による圧力損失[kPa]
        # tdb   :外気乾球温度['C]
        self.tout_ch_d = float(spec_table.iat[1,0])
        self.tin_ch_d = float(spec_table.iat[1,1])
        self.g_ch_d = float(spec_table.iat[1,2])
        # 定格冷凍容量[kW]
        self.q_ch_d = (self.tin_ch_d - self.tout_ch_d)*self.g_ch_d*1000*4.186/60
        # 定格主電動機入力[kW]
        self.pw_d = float(spec_table.iat[1,3])
        self.kr_ch = float(spec_table.iat[1,4])
        # 補機電力[kW]
        self.pw_sub = 0
        # 定格冷凍機COP
        self.COP_rp = self.q_ch_d / self.pw_d
        # 以下、毎時刻変わる可能性のある値
        self.tout_ch = 7
        self.pw = 0
        self.q_ch = 0
        self.pl = 0 # 負荷率(0.0~1.0)
        self.cop = 0
        self.flag = 0 #問題があったら1,なかったら0
        self.dp_ch = 0
        self.tin_ch = 7
        self.g_ch = 0
        self.tin_ch = 15
        self.tout_ch = 7
        self.tout_ch_sv = 7
        
        pl_cop = spec_table.drop(spec_table.index[[0, 1, 2]])
        pl_cop.iat[0,0] = '-'
        pl_cop = pl_cop.dropna(how='all', axis=1)
        self.data = pl_cop.values

        
    # 機器特性表に基づく空冷HPのCOPの算出
    def cal(self,tout_ch_sv, tin_ch, g_ch, tdb):
        self.flag = 0
        self.tout_ch_sv = tout_ch_sv
        self.tin_ch = tin_ch
        self.g_ch = g_ch
        # 冷水出口温度[℃]
        self.tout_ch = self.tout_ch_sv
        # 冷凍熱量[kW]
        self.q_ch = (self.tin_ch - self.tout_ch)*self.g_ch*1000*4.186/60

        if self.q_ch > 0:
             
            pl = self.data[0][1:].astype(np.float32)
            temp = self.data.transpose()[0][1:].astype(np.float32)
            dataset = self.data[1:].transpose()[1:].transpose().astype(np.float32)
            cop = RegularGridInterpolator((temp, pl), dataset)
            
            # 部分負荷率 現在は負荷率100%以上でも冷水出口温度は設定値が保たれるものとしている。
            self.pl = self.q_ch / self.q_ch_d
            pl_cop = self.pl
            if self.pl > pl[-1]:
                self.pl = pl[-1]
                pl_cop = self.pl
                self.tout_ch += (self.q_ch - self.q_ch_d)/(self.g_ch*1000*4.186/60)
                self.q_ch = self.q_ch_d
                self.flag = 1

            elif self.pl < pl[0]:
                pl_cop = pl[-1]
                self.flag = 2
        

            self.cop = float(cop([[tdb, pl_cop]]))
            self.pw = self.q_ch / self.cop + self.pw_sub
            
            
        elif self.q_ch == 0:
            self.pw = 0
            self.cop = 0
            self.pl = 0
            self.flag = 0
        else:
            self.pw = 0
            self.cop = 0
            self.pl = 0
            self.flag = 1
        
        self.dp_ch = -self.kr_ch*g_ch**2


# 冷却塔
class CoolingTower:
    def __init__(self, ua=143000, kr=1.0):
        # ua        :交換面積
        # g_w       :冷却水流量[kg/s]
        # g_a       :風量[kg/s]
        # tin_w     :冷却水入口温度[℃]
        # t_da      :外気乾球温度[℃]
        # rh        :外気相対湿度(0~100)
        # inv       :ファンインバーター周波数比（0.0~1.0）
        # flag      :収束計算確認のフラグ
        self.ua = ua
        self.kr = kr
        self.g_w = 0
        self.tin_w = 15
        self.g_a = 0
        self.t_da = 15
        self.rh = 50
        self.inv = 0
        self.flag = 0
        self.pw = 0
        self.dp = 0
        self.tout_w = 15
        
    def cal(self, g_w, Twin, Tda, rh):
        # cpw       :冷却水の比熱 [J/kg'C]
        # cp        :湿り空気（外気）の比熱 [J/kg'C]
        self.g_w = g_w
        self.Tda = Tda
        self.rh = rh
        self.tin_w = Twin
        self.g_a = self.inv*2000 # [m3/min]。ここで風量を与えてしまう
        self.pw = -35.469 * self.inv**3 + 59.499 * self.inv**2 - 1.6185 * self.inv + 0.7 #[kW]ここで計算してしまう
        if self.g_a < 10: # natural wind
            self.g_a = 10
            
        # 単位換算([m3/min] -> [kg/s])
        g_w = self.g_w * 10**3 / 60
        g_a = self.g_a * 1.293 / 60
        cpw = 4184
        cp = 1100
        
        if g_w > 0:
        
            # 乾球温度と湿球温度から外気比エンタルピーを求める
            [hin,xin] = tdb_rh2h_x(Tda,rh)
            Twbin = tdb_rh2twb(Tda,rh)
            
            # 湿球温度の飽和空気の比エンタルピーを求める
            # print(Twin,Twbin)
            # 空気出口湿球温度の最大値・最小値
            Twboutmax = max(Twin,Twbin);
            Twboutmin = min(Twin,Twbin);
            
            # 収束計算に入るための適当な初期値設定
            Twbout0 = 1;
            Twbout = 0;
            cnt = 0
            self.flag = 0
            
            while (Twbout0 - Twbout < - 0.01)or(Twbout0 - Twbout > 0.01):
    
                # 空気出口湿球温度の仮定
                Twbout0 = (Twboutmax + Twboutmin) / 2
                
                # 出口空気は飽和空気という仮定で、出口空気の比エンタルピーを求める。
                [hout, xout] = tdb_rh2h_x(Twbout0,100)
                
                # 空気平均比熱cpeの計算
                dh = hout - hin
                dTwb = Twbout0 - Twbin
                cpe = dh / dTwb
            
                ua_e = self.ua * cpe / cp
                
                Cw = g_w * cpw
                Ca = g_a * cpe
                Cmin = min(Cw,Ca)
                Cmax = max(Cw,Ca)
                if Cmin == 0:      # 苦肉の策
                    Cmin = 0.001
                if Cmax == 0:
                    Cmax = 0.001
                    
                NTU = ua_e / Cmin
                
                eps = (1 - math.exp(-NTU * (1 - Cmin / Cmax))) / (1 - Cmin / Cmax * math.exp(-NTU * (1 - Cmin / Cmax)))
                
                Q = eps * Cmin * (Twin - Twbin)
                
                Twbout = Twbin + Q / Ca
            
                if Twbout < Twbout0:
                    Twboutmax = Twbout0
                else:
                    Twboutmin = Twbout0
                
                cnt += 1
                if cnt > 30:
                    self.flag = 1
                    break
            
            self.tout_w = Twin - Q / Cw
        
        self.dp = -self.kr*self.g_w**2
        
        return self.tout_w
    
    def f2p(self,g_w):
        self.g_w = g_w
        self.dp = -self.kr_w*self.g_w**2
        return self.dp
        
    def f2p_co(self):
        return [0,0,-self.kr]

# 簡易なAHUモデル
class AHU_simple:
    def __init__(self, kr=1.0):
        # kr_eq     :圧力損失係数
        # q_load    :負荷熱量[MJ/min]
        # q         :処理熱量[MJ/min]
        self.kr = kr
        self.g = 0
        self.dp = 0
        self.tin = 15
        self.tout = 15
        self.q_load = 0
        self.q = 0
        self.flag = 0
    
    def cal(self,g,tin,q_load):
        self.g = g
        self.tin = tin
        self.q_load = q_load
        self.flag = 0
        if self.g > 0:
            self.tout = self.tin + q_load / 4.184 / self.g
        else:
            self.tout = self.tin
            
        if self.tout > 25:
            self.tout = 25
            self.flag = 1
            
        self.q = (self.tout - self.tin) * self.g * 4.184
        
        self.dp = -self.kr*self.g**2
        
        return self.tout
    
    def f2p(self,g):
        self.g = g
        self.dp = -self.kr*self.g**2
        return self.dp
    
    def f2p_co(self):
        return [0,0,-self.kr]


# 水-空気熱交換器
class W2a_hex():
    # HVACSIM+
    # 宇田川光弘：パソコンによる空気調和計算法，オーム社，p.8-219，1986 年.
    # 富樫 英介 : Popolo.2.2.0_熱環境計算戯法, 第8-9章, 2016 年.
    def __init__(self, rated_g_air=2.5, rated_v_air=2.99, rated_tdbin_air=27.2, rated_twbin_air=20.1,
                 rated_g_water=1.9833333, rated_v_water=1.25, rated_tin_water=7, rated_q=40.4, rated_rh_border=95):
        # q_load    :負荷熱量[GJ/min]
        # _d        :定格
        # q         :熱交換能力[kw]
        # g         :流量[kg/s]
        # v         :速度[m/s]
        # t         :温度[℃]
        # in, out   :入口, 出口
        # db, wb    :乾球, 湿球
        # ntu       :移動単位数(熱容量流量に対する熱交換器の能力)[-]
        # eff       :熱通過有効度[-]
        # rh_border :境界湿度[%]
        self.rated_v_water = rated_v_water
        self.rated_v_air = rated_v_air
        self.rated_g_air = rated_g_air
        self.rated_g_water = rated_g_water
        self.rated_tdbin_air = rated_tdbin_air
        self.rated_twbin_air = rated_twbin_air
        self.win_air = tdb_twb2w(self.rated_tdbin_air, self.rated_twbin_air)
        self.rated_tin_water = rated_tin_water
        self.rated_q = rated_q
        self.rated_rh_border = rated_rh_border

        # heat transfer coefficient dry - kW/(m^2*K) wet - kW/[m^2*(kJ/kg)]
        self.rated_coef_dry = 1 / (4.72 + 4.91 * math.pow(self.rated_v_water, -0.8) + 26.7 * math.pow(self.rated_v_air, -0.64))
        self.rated_coef_wet = 1 / (10.044 + 10.44 * math.pow(self.rated_v_water, -0.8) + 39.6 * math.pow(self.rated_v_air, -0.64))

        # surface area
        self.rated_cpma = w2cpair(self.win_air)
        self.rated_cap_air = self.rated_g_air * self.rated_cpma
        self.rated_cap_water = self.rated_g_water * 4.186

        if self.rated_tdbin_air < self.rated_tin_water:
            # heating coil
            self.rated_cap_min = min(self.rated_cap_air, self.rated_cap_water)
            self.rated_cap_max = max(self.rated_cap_air, self.rated_cap_water)

            self.rated_eff = self.rated_q / self.rated_cap_min / (self.rated_tin_water - self.rated_tdbin_air)
            self.rated_ntu = hex_ntu(self.rated_eff, self.rated_cap_min, self.rated_cap_max, 'counterflow')
            self.area_surface = self.rated_ntu * self.rated_cap_min / self.rated_coef_dry
        else:
            # cooling coil
            self.rated_tout_water = self.rated_tin_water + self.rated_q / self.rated_cap_water
            self.rated_hin_air = tdb_w2h(self.rated_tdbin_air, self.win_air)
            self.rated_hout_air = self.rated_hin_air - self.rated_q / self.rated_g_air

            # wet condition
            self.rated_wout_air = h_rh2w(self.rated_hout_air, self.rated_rh_border)

            if self.win_air < self.rated_wout_air:
                # dry condition
                self.rated_tout_air = self.rated_tdbin_air - self.rated_q / self.rated_cap_air
                self.rated_d1 = self.rated_tdbin_air - self.rated_tout_water
                self.rated_d2 = self.rated_tout_air - self.rated_tin_water
                self.rated_lmtd = (self.rated_d1 - self.rated_d2) / math.log(self.rated_d1 / self.rated_d2)
                self.area_surface = self.rated_q / self.rated_lmtd / self.rated_coef_dry
            else:
                # dry+wet condition
                # air condtion in border
                self.rated_t_border_air = w_rh2tdb(self.win_air, self.rated_rh_border)
                self.rated_h_border_air = tdb_w2h(self.rated_t_border_air, self.win_air)

                # water condition in border
                self.rated_h_border_wet = (self.rated_h_border_air - self.rated_hout_air) * self.rated_g_air
                self.rated_t_border_water = self.rated_tin_water + self.rated_h_border_wet / self.rated_cap_water

                # air saturation enthalpy that temperature equal to water
                self.rated_h_water_inlet = tdb2hsat(self.rated_tin_water)
                self.rated_h_border_water = tdb2hsat(self.rated_t_border_water)

                # dry surface
                self.rated_dt1 = self.rated_tdbin_air - self.rated_tout_water
                self.rated_dt2 = self.rated_t_border_air - self.rated_t_border_water
                self.rated_lmtd = (self.rated_dt1 - self.rated_dt2) / math.log(self.rated_dt1 / self.rated_dt2)
                self.rated_area_dry_sur = (self.rated_q - self.rated_h_border_wet) / self.rated_lmtd / self.rated_coef_dry

                # wet surface
                self.rated_dh1 = self.rated_h_border_air - self.rated_h_border_water
                self.rated_dh2 =self.rated_hout_air - self.rated_h_water_inlet
                self.rated_lmhd = (self.rated_dh1 - self.rated_dh2) / math.log(self.rated_dh1 / self.rated_dh2)
                self.rated_area_wet_sur = self.rated_h_border_wet / self.rated_lmhd / self.rated_coef_wet

                self.area_surface = self.rated_area_dry_sur + self.rated_area_wet_sur

    def coil_cal(self, tdb_in_air, win_air, rh_border, tin_water, g_air, g_water, coolingcoil, heatingcoil):
        # simulation input
        self.tdb_in_air = tdb_in_air
        self.w_air_inlet =win_air
        self.rh_border = rh_border
        self.tin_water = tin_water
        self.g_air = g_air
        self.g_water = g_water
        # output
        self.tout_air = 0
        self.wout_air = 0
        self.tout_water = 0
        self.ratio_drywet = 0
        self.coolingcoil = coolingcoil
        self.heatingcoil = heatingcoil

        self.t_border_water = self.t_border_air = 0
        self.zd = self.wd = self.v1 = self.v2 = self.zw = self.ww = self.v3 = self.v4 = self.v5 = self.v6 = 0
        if self.g_air <= 0 or self.g_water <= 0 or self.tdb_in_air == self.tin_water:
            self.tout_air = self.tdb_in_air
            self.tout_water = self.tin_water
            self.wout_air = self.w_air_inlet
            self.rhout_air = w_tdb2rh(self.wout_air, self.tout_air)
            self.ratio_drywet = 1
            q = 0
            return self.tout_air, self.wout_air, self.rhout_air, self.tout_water, self.ratio_drywet, q, self.g_water

        # capacity of water and wet air [kW/s]
        self.cpma = w2cpair(self.w_air_inlet)
        self.cap_air = self.g_air * self.cpma
        self.cap_water = self.g_water * 4.186

        # heat transfer coefficient dry - kW/(m^2*K) wet - kW/[m^2*(kJ/kg)]
        # proportion with water/air speed
        self.v_water = (self.g_water / self.rated_g_water) * self.rated_v_water
        self.v_air = (self.g_air / self.rated_g_air) * self.rated_v_air
        self.coef_dry = 1 / (4.72 + 4.91 * math.pow(self.v_water, -0.8) + 26.7 * math.pow(self.v_air, -0.64))
        self.coef_wet = 1 / (10.044 + 10.44 * math.pow(self.v_water, -0.8) + 39.6 * math.pow(self.v_air, -0.64))

        if self.tdb_in_air < self.tin_water:
            self.heatingcoil = 1
            ratio_drywet = 1

            cap_min = min(self.cap_air, self.cap_water)
            cap_max = max(self.cap_air, self.cap_water)
            ntu = self.coef_dry * self.area_surface / cap_min
            # efficient of heat gain
            eff = hex_effectiveness(ntu, cap_min / cap_max, 'counterflow')
            # outlet condition and heat change
            q = eff * cap_min * (self.tin_water - self.tdb_in_air)
            tout_air = self.tdb_in_air + q / self.cap_air
            tout_water = self.tin_water - q / self.cap_water
            wout_air = self.w_air_inlet
            rhout_air = w_tdb2rh(wout_air, tout_air)

        else:
            # cooling
            # consider as saturate temperature
            self.coolingcoil = 1
            t_border = w_rh2tdb(self.w_air_inlet, self.rh_border)
            hin_air = tdb_w2h(self.tdb_in_air, self.w_air_inlet)

            # saturation enthalpy based on Tdb
            # p_a parameter of temperature
            # p_b slice
            [p_a, p_b] = getparameter_hex(self.tin_water)
            xd = 1 / self.cap_air
            yd = -1 / self.cap_water
            xw = 1 / self.g_air
            yw = -p_a / self.cap_water

            def efunc(fdrate):

                self.zd = math.exp(self.coef_dry * self.area_surface * fdrate * (xd + yd))
                self.wd = self.zd * xd + yd
                self.v1 = xd * (self.zd - 1) / self.wd
                self.v2 = self.zd * (xd + yd) / self.wd

                self.zw = math.exp(self.coef_wet * self.area_surface * (1 - fdrate) * (xw + yw))
                self.ww = self.zw * xw + yw
                self.v3 = (xw + yw) / self.ww
                self.v4 = xw * (self.zw - 1) / self.ww
                self.v5 = self.zw * (xw + yw) / self.ww
                self.v6 = yw * (1 - self.zw) / self.ww / p_a

                self.t_border_water = (self.v5 * self.tin_water + self.v6 * (
                            hin_air - self.v1 * self.cpma * self.tdb_in_air - p_b)) \
                                      / (1 - self.v1 * self.v6 * self.cpma)
                self.t_border_air = self.tdb_in_air - self.v1 * (self.tdb_in_air - self.t_border_water)
                if fdrate == 1 and self.t_border_air > t_border:
                    return 1
                return t_border - self.t_border_air

            drate = 1

            if 0 < efunc(drate):
                try:
                    drate = optimize.brentq(efunc, 0, 1, xtol=0.0001, maxiter=100)  # brack=(0, 1) tol=0.0001,
                except ValueError:
                    drate = 0
                    efunc(drate)

            # outlet condition
            tout_water = self.tdb_in_air - self.v2 * (self.tdb_in_air - self.t_border_water)
            h_border_air = self.cpma * (self.t_border_air - self.tdb_in_air) + hin_air
            h_water_inlet = p_a * self.tin_water + p_b
            hout_air = self.v3 * h_border_air + self.v4 * h_water_inlet
            q = self.cap_air * (self.tdb_in_air - self.t_border_air) + self.g_air * (h_border_air - hout_air)
            ratio_drywet = drate

            if drate < 1:
                wout_air = h_rh2w(hout_air, self.rh_border)
            else:
                wout_air = self.w_air_inlet

            tout_air = w_h2tdb(wout_air, hout_air)
            rhout_air = w_tdb2rh(wout_air, tout_air)

        return tout_air, wout_air, rhout_air, tout_water, self.ratio_drywet, q, self.g_water, self.area_surface

    
# ダンパ特性と圧力損失計算
class Damper():
    def __init__(self, coef = [[1.0, 0.0000203437802163088], [0.8, 0.0000495885440290287],
                    [0.6, 0.000143390887269431], [0.4, 0.000508875127863876], [0.2, 0.00351368187709778]]):
        # damp  :ダンパ開度[0.0~1.0]
        # dp    :圧力損失[kPa]  # 単位注意
        # g     :流量[m^3/min]
        # dp = a * g^2
        # coef = [[damp1, a_damp1], ... , [dampn, a_dampnf2p]]
        # (x1 >...> xn, n>=3)
        self.coef = coef
        self.g = 0
        self.damp = 0
        self.dp = 0

    def f2p(self, damp, g):
        n = len(self.coef)
        self.g = g
        self.damp = damp
        if damp >= self.coef[0][0]:
            self.dp = self.coef[0][1] * self.g ** 2  # [kPa]
        elif damp <= self.coef[n - 1][0]:
            self.dp = self.coef[n - 1][1] * self.g ** 2  # [kPa]
        else:
            for i in range(1, n):  # 線形補間の上限・下限となる曲線を探す
                coef_a = self.coef[i - 1]  # higher limit curve
                coef_b = self.coef[i]  # lower limit curve
                if coef_b[0] <= self.damp < coef_a[0]:
                    break
            a = coef_a[1] * self.g ** 2
            b = coef_b[1] * self.g ** 2
            self.dp = (a - b) / (coef_a[0] - coef_b[0]) * (self.damp - coef_b[0]) + b
        
        if g >= 0:
            self.dp = self.dp
        else:
            self.dp = -self.dp
            
        return self.dp

    def p2f(self, damp, dp):
        n = len(self.coef)
        self.dp = abs(dp)
        self.damp = damp
        if damp >= self.coef[0][0]:
            self.g = pow(self.dp/self.coef[0][1], 0.5)
        elif damp <= self.coef[n - 1][0]:
            self.g = pow(self.dp/self.coef[n - 1][1], 0.5)
        else:
            for i in range(1, n):  # 線形補間の上限・下限となる曲線を探す
                coef_a = self.coef[i - 1]  # higher limit curve
                coef_b = self.coef[i]  # lower limit curve
                if coef_b[0] <= self.damp < coef_a[0]:
                    break
            a = pow(self.dp/coef_a[1], 0.5)
            b = pow(self.dp/coef_b[1], 0.5)
            self.g = (a - b) / (coef_a[0] - coef_b[0]) * (self.damp - coef_a[0]) + a
        
        if dp >= 0:
            self.g = self.g
        else:
            self.g = -self.g
            
        return self.g

    
# ファン特性と消費電力計算
class Fan:
    # 定格値の入力
    def __init__(self, pg=[0.6467, 0.0082, -0.0004], eg=[-0.0166, 0.0399, -0.0008], r_ef=0.8, inv=1.0):
        # pg    :圧力-流量(pg)曲線の係数（切片、一次、二次）
        # eg    :効率-流量(eg)曲線の係数（切片、一次、二次）
        # r_ef  :定格時の最高効率(本来は計算によって求める？)rated efficiency
        # inv   :回転数比(0.0~1.0)
        # dp_f  :ファン揚程[kPa]
        # g     :流量[m3/min]
        # pw    :消費電力[kW]
        # flag  :計算に問題があったら1、なかったら0
        # ef    :効率(0.0~1.0)
        self.pg = pg
        self.eg = eg
        self.r_ef = r_ef
        self.inv = inv
        self.dp = 0
        self.g = 0
        self.ef = 0
        self.pw = 0
        self.flag = 0
        self.num = 1

    def f2p(self, g):  # flow to pressure for fan
        self.g = g
        # 流量がある場合のみ揚程を計算する
        if self.g > 0:
            self.dp = (self.pg[0] + self.pg[1] * (self.g / self.inv) + self.pg[2] * (
                    self.g / self.inv) ** 2) * self.inv ** 2
        else:
            self.dp = 0

        if self.dp < 0:
            self.dp = 0
            self.flag = 1
        else:
            self.flag = 0

        return self.dp

    def f2p_co(self):  # coefficient for f2p
        return [self.pg[0] * self.inv ** 2, self.pg[1] * self.inv, self.pg[2]]

    def cal(self):
        # 流量がある場合のみ消費電力を計算する
        if self.g > 0 and self.inv > 0:

            # G: INV=1.0時（定格）の流量
            G = self.g / self.inv
            # K: 効率換算係数
            K = 1.0 - (1.0 - self.r_ef) / (self.inv ** 0.2) / self.r_ef
            # ef: 効率
            self.ef = K * (self.eg[0] + self.eg[1] * G + self.eg[2] * G ** 2)

            self.dp = (self.pg[0] + self.pg[1] * (self.g / self.inv) + self.pg[2] * (
                    self.g / self.inv) ** 2) * self.inv ** 2
            if self.dp < 0:
                self.dp = 0
                self.flag = 1

            #  軸動力を求める
            if self.ef > 0:
                self.pw = 1.0 * self.g * self.dp / (60 * self.ef)
                self.flag = 0
            else:
                self.pw = 0
                self.flag = 2

        else:
            self.pw = 0.0
            self.flag = 0
    

# 制御関係モデル ###############################################################

# pid制御（プログラムの中身はd成分を無視したpi制御）
class PID:
    # def __init__()の中の値はデフォルト値。指定しなければこの値で計算される。
    def __init__(self, mode=1, a_max=1, a_min=0, kp=0.8, ti=10, sig=0, t_reset=30, kg=1, t_step=1):
        # mode          :運転時1, 非運転時0
        # a_max,a_min   :制御値の最大・最小範囲
        # kp            :比例ゲイン
        # ti            :積分時間
        # sv            :現時刻の制御する要素の設定値 (温度や圧力)  S0:前時刻(S0は不使用)
        # mv            :現時刻の制御する要素の値   P0:前時刻(P0は不使用)
        # sig           :積分総和
        # a             :現時刻の制御に使用する要素の値(周波数比、バルブ開度など)
        # ctrl          :制御に使用する要素の制御量
        # kg            :CTRLの量を制御する要素の設定値に落とし込むための係数。(-1か1)
        # t_reset       :設定値に不全がある、または不具合で制御が長時間おかしくなっていた場合にSIGをリセットするまでの時間
        # t_step        :制御ステップ。1だと毎時刻制御出力する、2だと2時刻ごとに制御出力する。
        # example kp=0.06,ti=20
        self.mode = mode
        self.a_max = a_max
        self.a_min = a_min
        self.kp = kp
        self.ti = ti
        self.flag_reset = np.zeros(t_reset)
        self.kg = kg
        self.sig = sig
        self.t_step = t_step
        self.t_step_cnt = -1 # 計算ステップのための内部パラメータ
        self.a = 0     
        
        
    def control(self, sv, mv):
        if self.mode == 1:
            
            self.t_step_cnt += 1
            if self.t_step_cnt % self.t_step == 0:
                self.t_step_cnt = 0
            
                self.sig += sv  - mv
                ctrl = self.kp * ((sv - mv) + 1 / self.ti * self.sig)
                
                # 前時刻からの偏差は5%未満とする
                if ctrl > 0.05:
                    ctrl = 0.05
                elif ctrl < -0.05:
                    ctrl = -0.05
                    
                self.a = self.a + ctrl * self.kg
        
                # 制御量は上下限値をもつ
                if self.a > self.a_max:
                    self.a = self.a_max
                elif self.a < self.a_min:
                    self.a = self.a_min
                    
                # 積分時間リセット
                t_reset = self.flag_reset.size
                for ii in range(t_reset - 1, 0, -1):
                    self.flag_reset[ii] = self.flag_reset[ii - 1]
                if sv - mv > 0:
                    self.flag_reset[0] = 1
                elif sv - mv < 0:
                    self.flag_reset[0] = -1
                else:
                    self.flag_reset[0] = 0
            
                if all(i == 1 for i in self.flag_reset) == True or all(i == -1 for i in self.flag_reset) == True:
                    self.sig = 0
                    self.flag_reset = np.zeros(t_reset)
            
            
        elif self.mode == 0:
            self.a = 0
            
        return self.a

# バイパス弁を有するポンプについて、バイパス弁の開閉判断とPI制御を行う
class PumpWithBypassValve: # コンポジションというpython文法を使う
    def __init__(self, pump_pid, valve_pid, t_wait=15):
        # pump_pid      :ポンプのPID制御
        # valve_pid     :バイパス弁のPID制御
        # t_wait        :バイパス弁開閉切り替えの効果待ち時間[min]
        # a_min         :バイパス弁開閉判定の閾値として利用する
        # flag_switch   :バイパス弁開閉判定のための配列
        # switch        :0=ポンプのみ、1=バイパス弁開
        self.pump_pid = pump_pid
        self.valve_pid = valve_pid
        self.t_wait = t_wait
        self.flag_switch = np.zeros(self.t_wait)
        self.switch = 0
        self.sv = 0
        self.mv = 0
        
    def control(self, sv, mv):
        self.sv = sv
        self.mv = mv
        
        for i in range(self.t_wait - 1, 0, -1):
            self.flag_switch[i] = self.flag_switch[i-1]
        # switch判定 pump_pid.aには前時刻の値が残っている
        if self.switch == 0 and self.pump_pid.a == self.pump_pid.a_min:
            self.flag_switch[0] = 1
        elif self.switch == 0:
            self.flag_switch[0] = 0
        elif self.switch == 1 and self.valve_pid.a == self.valve_pid.a_min:
            self.flag_switch[0] = 0
        elif self.switch == 1:
            self.flag_switch[0] = 1
                
        
        if self.switch == 1 and all(i == 0 for i in self.flag_switch):
            self.switch = 0
            self.valve_pid.sig = 0 #切り替わる際に積分リセット（安定性向上のため）
            self.pump_pid.sig = 0
        elif self.switch == 0 and all(i == 1 for i in self.flag_switch):
            self.switch = 1
            self.valve_pid.sig = 0
            self.pump_pid.sig = 0
            
        if self.switch == 0:
            self.valve_pid.a = 0
            self.pump_pid.mode = 1
            self.pump_pid.control(sv=self.sv,mv=self.mv)
        
        elif  self.switch == 1:
            self.valve_pid.control(sv=self.sv,mv=self.mv)
            self.pump_pid.mode = 1
            self.pump_pid.a = self.pump_pid.a_min
        
        return [self.pump_pid.a, self.valve_pid.a]

# 冷却塔バイパス弁といった、ポンプとは別の制御目標値を持っているバイパス弁の開閉判定とPI制御。
class BypassValve: # コンポジションというpython文法を使う
    def __init__(self, valve_pid, t_wait=15, mode=0):
        # valve_pid     :バイパス弁のPID制御
        # t_wait        :バイパス弁開閉切り替えの効果待ち時間[min]
        # mv_min, max   :バイパス弁の開閉判定の閾値
        # mode          :0=mvが小さくなったらバイパス弁開、1=mvが大きくなったらバイパス弁開
        # switch        :0=バイパス弁閉、1=バイパス弁開
        self.valve_pid = valve_pid
        self.t_wait = t_wait
        self.flag_switch = np.zeros(self.t_wait)
        self.mode = mode
        self.thre = 0
        self.switch = 0
        
    def control(self, sv, mv, thre):
        self.sv = sv
        self.mv = mv
        self.thre = thre
        
        # switch判定 valve_pid.aには前時刻の値が残っている   
        for i in range(self.t_wait - 1, 0, -1):
            self.flag_switch[i] = self.flag_switch[i-1]
        if self.mode == 0:
            if self.switch == 0 and self.mv <= self.thre:
                self.flag_switch[0] = 1
            elif self.switch == 0:
                self.flag_switch[0] = 0
            elif self.switch == 1 and self.valve_pid.a == self.valve_pid.a_min:
                self.flag_switch[0] = 0
            elif self.switch == 1:
                self.flag_switch[0] = 1
        elif self.mode == 1:
            if self.switch == 0 and self.mv >= self.thre:
                self.flag_switch[0] = 1
            elif self.switch == 0:
                self.flag_switch[0] = 0
            elif self.switch == 1 and self.valve_pid.a == self.valve_pid.a_min:
                self.flag_switch[0] = 0
            elif self.switch == 1:
                self.flag_switch[0] = 1
        
        if self.switch == 1 and all(i == 0 for i in self.flag_switch):
            self.switch = 0
            self.valve_pid.sig = 0 #切り替わる際に積分リセット（安定性向上のため）
        elif self.switch == 0 and all(i == 1 for i in self.flag_switch):
            self.switch = 1
            self.valve_pid.sig = 0
            
        if self.switch == 0:
            self.valve_pid.a = 0
        
        elif  self.switch == 1:
            self.valve_pid.control(sv=self.sv,mv=self.mv)
       
        return self.valve_pid.a

# 増減段閾値と効果待ち時間を有する台数制御   
class UnitNum:
    def __init__(self, thre_up=[0.5,1.0], thre_down=[0.4,0.9], t_wait=15, num=1):
        # thre_up       :増段閾値(1->2, 2->3といった時の値。型は配列またはリストとする) thre: threshold, g: 流量, q: 熱量
        # thre_down     :減段閾値(2->1, 3->2といった時の値。型は配列またはリストとする)
        # t_wait        :効果待ち時間(ex: 15分)
        # num           :運転台数 num: number
        # g             :流量[m3/min] ここでは流量gに基づき台数制御するとしているが、他の変数でも適用可能
        self.thre_up = thre_up
        self.thre_down = thre_down
        self.t_wait = t_wait
        self.num = num
        self.flag_switch = np.ones(t_wait)*num
        self.g = 0
            
    def control(self, g):
        self.g = g
        num_max = len(self.thre_up)+1
        
        for i in range(self.t_wait - 1, 0, -1):
            self.flag_switch[i] = self.flag_switch[i-1]
          
        if self.num == num_max:
            if self.g < self.thre_down[self.num-2]:
                self.flag_switch[0] = self.num-1
        elif self.num == 1:
            if self.g > self.thre_up[self.num-1]:
                self.flag_switch[0] = self.num+1
                
        elif self.g > self.thre_up[self.num-1]:
            self.flag_switch[0] = self.num+1
        elif self.g < self.thre_down[self.num-2]:
            self.flag_switch[0] = self.num-1
        else:
            self.flag_switch[0] = self.num
            
        if self.flag_switch[0] < 1:
            self.flag_switch[0] = 1
        elif self.flag_switch[0] > num_max:
            self.flag_switch[0] = num_max
        
            
        if all(i > self.num for i in self.flag_switch):
            self.num += 1
        elif all(i < self.num for i in self.flag_switch):
            self.num -= 1
        
        return self.num
    
# 冷凍機台数制御
class UnitNumChiller:
    def __init__(self, thre_up_g=[0.5,1.0], thre_down_g=[0.4,0.9], thre_up_q=[0.5,1.0], thre_down_q=[0.4,0.9],t_wait=15):
        # thre_up_g     :増段閾値(1->2, 2->3といった時の値。型は配列またはリストとする) thre: threshold, g: 流量, q: 熱量
        # thre_down_q   :減段閾値(2->1, 3->2といった時の値。型は配列またはリストとする)
        # t_wait        :効果待ち時間(ex: 15分)
        # num           :運転台数 num: number
        # g             :流量[m3/min]
        # q             :熱量[kW]
        self.thre_up_g = thre_up_g
        self.thre_down_g = thre_down_g
        self.thre_up_q = thre_up_q
        self.thre_down_q = thre_down_q
        self.t_wait = t_wait
        self.num = 1
        self.flag_switch = np.zeros(t_wait)
        self.g = 0      
            
    def control(self, g, q):
        self.g = g
        self.q = q
        num_max = len(self.thre_up_g)+1
        flag_g = 0
        flag_q = 0
        
        for i in range(self.t_wait - 1, 0, -1):
            self.flag_switch[i] = self.flag_switch[i-1]
        
        # 熱量ベースの増減段指示
        if self.num == num_max:
            if self.q < self.thre_down_q[self.num-2]:
               flag_q = -1
        elif self.num == 1:
            if self.q > self.thre_up_q[self.num-1]:
                flag_q = 1         
        elif self.q > self.thre_up_q[self.num-1]:
            flag_q = 1
        elif self.g < self.thre_down_q[self.num-2]:
            flag_q = -1

        # 流量ベースの増減段指示
        if self.num == num_max:
            if self.g < self.thre_down_g[self.num-2]:
               flag_g = -1
        elif self.num == 1:
            if self.g > self.thre_up_g[self.num-1]:
                flag_g = 1         
        elif self.g > self.thre_up_g[self.num-1]:
            flag_g = 1
        elif self.g < self.thre_down_g[self.num-2]:
            flag_g = -1
        
        # 増減段指示
        if flag_g == 1 or flag_q == 1:
            self.flag_switch[0] = self.num+1
        elif flag_g == -1 and flag_q == -1:
            self.flag_switch[0] = self.num-1
        else:
            self.flag_switch[0] = self.num
        
        if all(i > self.num for i in self.flag_switch):
            self.num += 1
        elif all(i < self.num for i in self.flag_switch):
            self.num -= 1
        
        return self.num
                
# 流量計算関係モデル ###########################################################

# 機器のみを有する枝
class Branch00:
    # def __init__()の中の値はデフォルト値。指定しなければこの値で計算される。
    def __init__(self, kr_eq=0.8, kr_pipe=0.5, head_act=0):
        # g         :流量[m3/min]
        # dp        :枝の出入口圧力差[kPa]加圧：+, 減圧：-
        # kr_pipe   :管の圧損係数[kPa/(m3/min)^2]
        # kr_eq     :機器の圧損係数[kPa/(m3/min)^2]
        # vlv       :バルブ開度(1:全開,0:全閉)
        # head_act  :実揚程[kPa]
        self.kr_eq = kr_eq
        self.kr_pipe = kr_pipe
        self.dp = 0.0
        self.g = 0.0
        self.flag = 0
        self.head_act = head_act
        
    def f2p(self,g): # 流量から圧力損失を求める flow to pressure for branch
        self.g = g
        # (枝の圧損) = (管圧損) + (機器圧損)
        self.dp = -self.kr_pipe * self.g**2 - self.kr_eq * self.g**2 - self.head_act
        return self.dp
    
    def p2f(self, dp): # 圧力損失から流量を求める
        self.dp = dp
        self.flag = 0
        [co_0, co_1, co_2] = [- self.head_act - self.dp, 0, -self.kr_pipe - self.kr_eq]
        if co_1**2 - 4*co_2*co_0 > 0:
            g1 = (-co_1 + (co_1**2 - 4*co_2*co_0)**0.5)/(2 * co_2)
            g2 = (-co_1 - (co_1**2 - 4*co_2*co_0)**0.5)/(2 * co_2)
            if max(g1, g2) < 0:
                self.g = 0.0
                self.flag = 1
            else:
                self.g = max(g1, g2)
        else:
            self.g = 0.0
            self.flag = 1  
        return self.g     

# 機器、バルブを有する枝
class Branch01: # コンポジションというpython文法を使う
    # def __init__()の中の値はデフォルト値。指定しなければこの値で計算される。
    def __init__(self, valve, kr_eq=0.8, kr_pipe=0.5):
        # g         :枝の出入口流量[m3/min]
        # dp        :枝の出入口圧力差[kPa]加圧：+, 減圧：-
        # kr_pipe      :管の圧損係数[kPa/(m3/min)^2]
        # kr_eq      :機器の圧損係数[kPa/(m3/min)^2]
        # valve     :バルブのオブジェクト
        # vlv       :バルブ開度(1:全開,0:全閉)
        self.valve = valve
        self.kr_eq = kr_eq
        self.kr_pipe = kr_pipe
        self.dp = 0.0
        self.g = 0.0
        self.flag = 0
        
    def f2p(self, g): # 流量から圧力損失を求める
        # (枝の圧損) = (管圧損) + (機器圧損) + (バルブ圧損) 
        self.g = g
        self.dp = - self.kr_pipe * self.g**2 - self.kr_eq * self.g**2 + self.valve.f2p(self.g)
        return self.dp
    
    def p2f(self, dp): # 圧力差から流量を求める
        self.dp = dp
        self.flag = 0
        
        [co_0, co_1, co_2] = self.valve.f2p_co() + np.array([-self.dp, 0, -self.kr_pipe-self.kr_eq]) # 二次関数の係数の算出
        
        if co_1**2 - 4*co_2*co_0 > 0:
            g1 = (-co_1 + (co_1**2 - 4*co_2*co_0)**0.5)/(2 * co_2)
            g2 = (-co_1 - (co_1**2 - 4*co_2*co_0)**0.5)/(2 * co_2)
            if max(g1, g2) < 0:
                self.g = 0.0
                self.flag = 1
            else:
                self.g = max(g1, g2)
        else:
            self.g = 0.0
            self.flag = 1
        self.valve.g = self.g   
        return self.g
        
    
# ポンプ・機器を有する枝   
class Branch10: # コンポジションというpython文法を使う
    # def __init__()の中の値はデフォルト値。指定しなければこの値で計算される。
    def __init__(self, pump, kr_eq=0.8, kr_pipe=0.5):
        # pump      :ポンプのオブジェクト
        # kr_pipe   :管の圧損係数[kPa/(m3/min)^2]
        # kr_eq     :機器の圧損係数[kPa/(m3/min)^2]
        # dp        :枝の出入口差圧[kPa]加圧：+, 減圧：-
        # flag      :計算の順当性確認のためのフラグ
        self.pump = pump
        self.kr_eq = kr_eq
        self.kr_pipe = kr_pipe
        self.dp = 0.0
        self.g = 0.0
        self.flag = 0
    
    def f2p(self, g):        
        if self.pump.inv == 0: #　ポンプ停止時の対応
            self.dp = 0.0
        else:
            self.g = g
            # 枝の出入口差圧=ポンプ加圧-配管圧損-機器圧損
            self.dp = self.pump.f2p(self.g) - self.kr_pipe*self.g**2 - self.kr_eq*self.g**2
        
        return self.dp
        
    def p2f(self, dp): # 圧力差から流量を求める
        
        if self.pump.inv == 0: #　ポンプ停止時の対応
            self.g = 0.0
        else:
            self.dp = dp
            self.flag = 0
            [co_0, co_1, co_2] = self.pump.f2p_co() + np.array([-self.dp, 0, -self.kr_pipe-self.kr_eq]) # 二次関数の係数の算出
            if co_1**2 - 4*co_2*co_0 > 0:
                g1 = (-co_1 + (co_1**2 - 4*co_2*co_0)**0.5)/(2 * co_2)
                g2 = (-co_1 - (co_1**2 - 4*co_2*co_0)**0.5)/(2 * co_2)
                if max(g1, g2) < 0:
                    self.g = 0.0
                    self.flag = 1
                else:
                    self.g = max(g1, g2)
            else:
                self.g = 0.0
                self.flag = 1
            self.pump.g = self.g
            
        return self.g
            

# 並列ポンプ複数台とバイパス弁を有する枝
class Branch11: # コンポジションというpython文法を使う
    def __init__(self, valve, pump, kr_pipe_pump=0.5, kr_pipe_valve=0.5):
        # pg            :ポンプ流量-圧損曲線係数
        # kr_pipe_pump  :ポンプ用管の圧損係数[kPa/(m3/min)^2]
        # dp            :枝の出入口差圧[kPa]加圧：+, 減圧：-
        # vlv           :バルブ開度(1:全開,0:全閉)
        # g             :枝の出入り流量
        # dp            :枝の出入り圧力差
        self.pump = pump
        self.valve = valve
        self.kr_pipe_pump = kr_pipe_pump
        self.kr_pipe_valve = kr_pipe_valve
        self.g = 0.0
        self.dp = 0.0
        self.flag = 0
        
    def f2p(self, g): # 流量から圧力損失を求める
        self.g = g
        self.flag = 0
        
        if self.valve.vlv == 0:
            self.valve.g = 0.0
            self.pump.g = self.g / self.pump.num
            self.dp = - self.kr_pipe_pump * self.pump.g**2 + self.pump.f2p(self.pump.g)
        if self.pump.inv == 0 and self.valve.vlv > 0:
            self.pump.g = 0.0
            self.valve.g = self.g
            self.dp = - self.kr_pipe_valve * self.valve.g**2 + self.valve.f2p(self.valve.g)
        else:
            [co_0a, co_1a, co_2a] = self.pump.f2p_co() + np.array([0, 0, -self.kr_pipe_pump]) # 二次関数の係数の算出
            [co_0b, co_1b, co_2b] = self.valve.f2p_co() + np.array([0, 0, -self.kr_pipe_valve])
            # co_0a + co_1a*self.pump.g + co_2a*self.pump.g**2 = - co_2b*self.valve.g**2
            # self.pump.num*self.pump.g - self.valve.g = self.g
            # 上記二式を変形した二次方程式の係数は以下のようになる
            [co_0c, co_1c, co_2c] = [co_0a + co_2b*self.g**2, co_1a - co_2b*2*self.pump.num*self.g, co_2a + co_2b*self.pump.num**2]

            if co_1c**2 - 4*co_2c*co_0c > 0:
                g1 = (-co_1c + (co_1c**2 - 4*co_2c*co_0c)**0.5)/(2 * co_2c)
                g2 = (-co_1c - (co_1c**2 - 4*co_2c*co_0c)**0.5)/(2 * co_2c)
                if max(g1, g2) < 0:
                    self.pump.g = 0.0
                    self.flag = 1
                else:
                    self.pump.g = max(g1, g2)
            else:
                self.pump.g = 0.0
                self.flag = 1
            
            self.valve.g = self.pump.num*self.pump.g - self.g
            self.dp = - self.kr_pipe_pump * self.pump.g**2 + self.pump.f2p(self.pump.g)
        
        return self.dp
        
# ポンプ、機器、バイパス弁を有する枝
class Branch12: # コンポジションというpython文法を使う
    def __init__(self, valve, pump, kr_eq=0.5, kr_pipe=0.5, kr_pipe_bypass=0.5):
        # valve         :バルブのオブジェクト
        # pump          :ポンプのオブジェクト
        # kr_pipe       :ポンプ・機器のある配管の圧損係数
        # dp            :枝の出入口圧力差[kPa]加圧：+, 減圧：-
        self.valve = valve
        self.pump = pump
        self.kr_eq = kr_eq
        self.kr_pipe = kr_pipe
        self.kr_pipe_bypass = kr_pipe_bypass
        self.g = 0.0
        self.dp = 0.0
        self.flag = 0
        
    def p2f(self, dp): # 圧力から流量を求める dp=0でも流れる？？
        self.dp = dp
        self.flag = 0
        if self.valve.vlv == 0 and self.pump.inv == 0:
            self.valve.g = 0.0
            self.pump.g = 0.0
            
        elif self.valve.vlv == 0:
            self.valve.g = 0
            [co_0, co_1, co_2] = self.pump.f2p_co() + np.array([-self.dp, 0, -self.kr_pipe-self.kr_eq])
            if co_1**2 - 4*co_2*co_0 > 0:
                g1 = (-co_1 + (co_1**2 - 4*co_2*co_0)**0.5)/(2 * co_2)
                g2 = (-co_1 - (co_1**2 - 4*co_2*co_0)**0.5)/(2 * co_2)
                if max(g1, g2) < 0:
                    self.pump.g = 0.0
                    self.flag = 1
                else:
                    self.pump.g = max(g1, g2)
            else:
                self.pump.g = 0
                self.flag = 1
                
        elif self.pump.inv == 0:
            self.pump.g = 0.0
            [co_0, co_1, co_2] = self.valve.f2p_co() + np.array([self.dp, 0, -self.kr_pipe_bypass])
            
            if co_2 < 0 and self.dp < 0:
                self.valve.g = (self.dp / co_2)**0.5
            elif co_2 < 0 and self.dp > 0:
                self.valve.g = -(self.dp / -co_2)**0.5 # 逆流する
            else:
                self.valve.g = 0.0
                self.flag = 2
            
        else:
            # ポンプの流量
            [co_0, co_1, co_2] = self.pump.f2p_co() + np.array([-self.dp, 0, -self.kr_pipe-self.kr_eq])
            if co_1**2 - 4*co_2*co_0 > 0:
                g1 = (-co_1 + (co_1**2 - 4*co_2*co_0)**0.5)/(2 * co_2)
                g2 = (-co_1 - (co_1**2 - 4*co_2*co_0)**0.5)/(2 * co_2)
                if max(g1, g2) < 0:
                    self.pump.g = 0.0
                    self.flag = 3
                else:
                    self.pump.g = max(g1, g2)
            else:
                self.pump.g = 0.0
                self.flag = 4
                
            # バイパス弁流量
            [co_0, co_1, co_2] = self.valve.f2p_co() + np.array([self.dp, 0, -self.kr_pipe_bypass])
            
            if co_2 < 0 and self.dp > 0:
                self.valve.g = (-self.dp / co_2)**0.5
            elif co_2 < 0 and self.dp < 0:
                self.valve.g = -(self.dp / co_2)**0.5 # 逆流する
            else:
                self.valve.g = 0.0
                self.flag = 5
            
        self.g = self.pump.g - self.valve.g
        
        return self.g




