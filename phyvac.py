# -*- coding: utf-8 -*-
"""
@author: shhmy
"""
# phyvacモジュール。hvac + python ->phyvac
# 空調システムの計算を極力物理原理・詳細な制御ロジックに基づいて行う。
# ver0.2 20210628

import math
import traceback
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator
from scipy import optimize
from sklearn.linear_model import LinearRegression

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
# 大気圧は1013.25 hPaではなく101.325 kPa!!!

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
        pv_2 = tdb2psat(twb) - 0.000662 * 101.325 * (tdb - twb)

        if pv_1 - pv_2 > 0:
            twb_min = twb
        else:
            twb_max = twb

        cnt += 1
        if cnt > 20:
            break

    return twb


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


# 乾球温度と湿球温度から絶対湿度[kg/kg']
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
         
        if self.g < 0:
            self.dp = -self.dp
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
class Pump():
    # 定格値の入力
    def __init__(self, pg=[233,5.9578,-4.95], eg=[0.0099,0.4174,-0.0508], r_ef=0.8, figure=1):
        # pg     :圧力-流量(pg)曲線の係数（切片、一次、二次）
        # eg     :効率-流量(eg)曲線の係数（切片、一次、二次）
        # r_ef   :定格時の最高効率(本来は計算によって求める？)rated efficiency
        # inv    :回転数比(0.0~1.0)
        # dp_p   :ポンプ揚程[kPa]
        # g_p    :流量[m3/min]
        # pw_p   :消費電力[kW]
        # flag   :計算に問題があったら1、なかったら0
        # ef     :効率(0.0~1.0)
        # para   :並列ポンプか否かのフラグ
        # figure :1だったらポンプの性能曲線を表示する、1でなかったら表示しない
        
        (filename, line_number, function_name, text) = traceback.extract_stack()[-2]
        self.name = text[:text.find('=')].strip()  # インスタンス名の取得、'__init__'の最初でなければならない
        
        self.pg = pg
        self.eg = eg
        self.r_ef = r_ef
        self.inv = 0.0
        self.dp = 0.0
        self.g = 0.0
        self.ef = 0.0
        self.pw = 0.0
        self.flag = 0
        self.para = 0
        
        if figure == 1:
            self.figure_curve()
    
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
            K = (1.0 - (1.0 - self.r_ef) / (self.inv**0.2)) / self.r_ef 
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
            
    def figure_curve(self):
        x_max, _ = quadratic_formula(self.pg[0], self.pg[1], self.pg[2])
        x = np.linspace(0, x_max * 0.8, 50)
        y_p = self.pg[0] + self.pg[1] * x + self.pg[2] * x ** 2
        y_e = self.eg[0] + self.eg[1] * x + self.eg[2] * x ** 2
        fig, ax1 = plt.subplots()
        color1 = 'tab:orange'
        ax1.set_xlabel('Flow [m3/min]')
        ax1.set_ylabel('Total Head [kPa]', color=color1)
        ax1.plot(x, y_p, color=color1)
        ax1.tick_params(axis='y', labelcolor=color1)
        ax1.set_ylim(0, self.pg[0] + 10)

        ax2 = ax1.twinx()
        color2 = 'tab:blue'
        ax2.set_ylabel('Efficiency [-]', color=color2)
        ax2.plot(x, y_e, color=color2)
        ax2.tick_params(axis='y', labelcolor=color2)
        ax2.set_ylim(0, 1)
        plt.title('{}'.format(self.name))

        return plt.show()
        
        
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
        self.pl = 0 # 負荷率(0.0~1.0)
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

        
# 省エネ基準に基づいた吸収式冷温水発生機モデル (Energy-Saving Standard) 
class AbsorptionChillerESS:
    # rated_capacity_c:     定格冷房能力 [kW]
    # rated_input_fuel_c:   定格冷房燃料消費量 [Nm3](燃料: 都市ガス)
    # power_c:              定格冷房消費電力 [kW]
    # rated_capacity_h:     定格暖房能力 [kW]
    # rated_input_fuel_h:   定格暖房燃料消費量 [Nm3](燃料: 都市ガス)
    # power_h:              定格暖房消費電力 [kW]

    def __init__(self, rated_capacity_c, rated_input_fuel_c, power_c,
                 rated_capacity_h, rated_input_fuel_h, power_h):

        self.rated_capacity_c = rated_capacity_c
        self.rated_input_fuel_c = rated_input_fuel_c
        self.power_c = power_c
        self.rated_capacity_h = rated_capacity_h
        self.rated_input_fuel_h = rated_input_fuel_h
        self.power_h = power_h

        self.cw_c = 4.192     # 10℃水の比熱, [kJ/(kg・k)]
        self.cw_h = 4.178     # 40℃水の比熱, [kJ/(kg・k)]
        self.rho_c = 999.741  # 10℃水の密度, [kg/m3]
        self.rho_h = 992.210  # 40℃水の密度, [kg/m3]
        self.cg = 40.6        # 都市ガス13A, 低位発熱量[MJ/m3N]
        self.k = 3.6          # MJ to kWh, [MJ/kWh]

        # 出力値
        # power_cとpower_hは計算できないため、そのまま出力 
        self.capacity_c = 0     # 冷房能力, [kW]
        self.input_fuel_c = 0   # 冷房燃料消費量, [Nm3]
        self.cop_c = 0          # 冷房運転COP, [-]
        self.tout_ch = 7        # 冷水出口温度, ℃
        
        self.capacity_h = 0     # 暖房能力, [kW]
        self.input_fuel_h = 0   # 暖房燃料消費量, [Nm3]
        self.cop_h = 0          # 暖房運転COP, [-]
        self.tout_h = 45        # 温水出口温度, ℃
        
    def cal_c(self, g, tin_cd=32, tin_ch=15, tout_ch_sv=7):
        # g:          冷水流量[m3/min]
        # tin_cd:     冷却水温度, ℃
        # tin_ch:     冷水入口温度, ℃
        # tout_ch_sv: 冷水出口温度設定値, ℃

        k_1 = 1  # 最大能力比特性
        capacity = self.rated_capacity_c * k_1  # 最大能力
        g = g * self.rho_c / 60  # 体積流量[m3/min] to 質量流量[kg/s]
        self.capacity_c = g * (tin_ch - tout_ch_sv) * self.cw_c  # 処理する熱量

        self.tout_ch = tout_ch_sv
        if self.capacity_c > self.rated_capacity_c:  # 処理熱量が定格能力より大きい時の冷水出口温度を求める
            delta_t = (self.capacity_c - self.rated_capacity_c) / (g * self.cw_c)
            self.tout_ch = tout_ch_sv + delta_t
            self.capacity_c = self.rated_capacity_c

        plr = self.capacity_c / capacity
        if plr > 1:
            plr = 1
        if plr < 0.2:
            plr = 0.2

        k_2 = 0.012333 * tin_cd + 0.605333  # 最大入力比
        k_3 = 0.167757 * plr ** 2 + 0.757814 * plr + 0.074429  # 入力比
        k_4 = -0.01276 * self.tout_ch + 1.0893  # 入力比
        self.input_fuel_c = self.rated_input_fuel_c * k_2 * k_3 * k_4  # 燃料消費量

        q_gas = self.input_fuel_c * self.cg / self.k  # 消費熱量
        self.cop_c = self.capacity_c / (q_gas + self.power_c)

        return self.capacity_c, self.input_fuel_c, self.cop_c, self.tout_ch, self.power_c

    def cal_h(self, g, tin_h=37, tout_h_sv=45):
        # g:          温水流量[m3/min]
        # tin_h:      温水入口温度, ℃
        # tout_h_sv:  温水出口温度設定値, ℃

        k_1 = 1  # 最大能力比特性
        capacity = self.rated_capacity_h * k_1   # 最大能力

        g = g * self.rho_h / 60  # 体積流量[m3/min] to 質量流量[kg/s]
        self.capacity_h = g * (tout_h_sv - tin_h) * self.cw_h

        self.tout_h = tout_h_sv
        if self.capacity_h > self.rated_capacity_h:
            delta_t = (self.capacity_h - self.rated_capacity_h) / (g * self.cw_h)
            self.tout_h = tout_h_sv - delta_t
            self.capacity_h = self.rated_capacity_h

        plr = self.capacity_h / capacity
        if plr > 1:
            plr = 1
        if plr < 0.1:
            plr = 0.1

        k_2 = 1
        k_3 = 1 * plr
        k_4 = 1
        self.input_fuel_h = self.rated_input_fuel_h * k_2 * k_3 * k_4
        q_gas = self.input_fuel_h * self.cg / self.k  # 消費熱量
        self.cop_h = self.capacity_h / (q_gas + self.power_h)

        return self.capacity_h, self.input_fuel_h, self.cop_h, self.tout_h, self.power_h


# 省エネ基準に基づいたVRFモデル (Energy-Saving Standard)　
class VariableRefrigerantFlowESS:
    def __init__(self, rated_capacity_c, rated_input_power_c, rated_capacity_h, rated_input_power_h):
        # rated_capacity_c:      定格冷房能力 [kW]
        # rated_input_power_c:   定格冷房消費電力 [kW]
        # rated_capacity_h:      定格暖房能力 [kW]
        # rated_input_fuel_h:    定格暖房消費電力 [kW]
        self.rated_capacity_c = rated_capacity_c
        self.rated_input_power_c = rated_input_power_c
        self.rated_capacity_h = rated_capacity_h
        self.rated_input_power_h = rated_input_power_h
        # 出力値
        self.capacity_c = 0
        self.input_power_c = 0
        self.cop_c = 0
        self.capacity_h = 0
        self.input_power_h = 0
        self.cop_h = 0

    # cooling mode
    def cal_c(self, odb, indoor_capacity):
        if odb < 15:   # 外気乾球温度の下限
            odb = 15
        if odb > 43:   # 外気乾球温度の上限
            odb = 43

        k_1 = -0.0025 * odb + 1.0875   # 能力比特性
        capacity_a = self.rated_capacity_c * k_1   # その外気条件での最大能力
        self.capacity_c = capacity_a

        cr = indoor_capacity / self.rated_capacity_c   # combination ratio: 室内機容量が室外機容量に示す比例
        if cr < 1:
            self.capacity_c = indoor_capacity
            if capacity_a < indoor_capacity:
                self.capacity_c = capacity_a

        plr = self.capacity_c / capacity_a  # 運転部分負荷率(その外気条件での最大能力に対する部分負荷率)
        if plr > 1:
            plr = 1
        if plr < 0.3:
            plr = 0.3

        k_2 = 0.0001212 * odb ** 2 + 0.00369 * odb + 0.72238   # 入力比特性
        k_3 = 0.8573 * plr ** 2 - 0.0456 * plr + 0.1883   # 部分負荷特性

        self.input_power_c = self.rated_input_power_c * k_2 * k_3
        self.cop_c = self.capacity_c / self.input_power_c

        return self.capacity_c, self.input_power_c, self.cop_c

    # heating mode
    def cal_h(self, owb, indoor_capacity):
        if owb < -20:  # 外気湿球温度の下限
            owb = -20
        if owb > 15:  # 外気湿球温度の上限
            owb = 15

        k_1 = 0  # 能力比特性
        if -20 <= owb <= -8:
            k_1 = 0.0255 * owb + 0.847
        if -8 < owb <= 4.5:
            k_1 = 0.0153 * owb + 0.762
        if 4.5 < owb <= 15:
            k_1 = 0.0255 * owb + 0.847
        capacity_a = self.rated_capacity_h * k_1
        self.capacity_h = capacity_a

        cr = indoor_capacity / self.rated_capacity_h
        if cr < 1:
            self.capacity_h = indoor_capacity
            if capacity_a < indoor_capacity:
                self.capacity_h = capacity_a

        plr = self.capacity_h / capacity_a
        if plr > 1:
            plr = 1
        if plr < 0.3:
            plr = 0.3

        k_2 = 0.0128 * owb + 0.9232  # 入力比特性
        k_3 = 0.7823 * plr ** 2 + 0.0398 * plr + 0.1779  # 部分負荷特性
        self.input_power_h = self.rated_input_power_h * k_2 * k_3
        self.cop_h = self.capacity_h / self.input_power_h

        return self.capacity_h, self.input_power_h, self.cop_h
    
 
# EnergyPlusに基づいたVRFモデル
# EnergyPlus Engineering Reference(22.1), Variable Refrigerant Flow Heat Pumps, System Curve based VRF Model
# Raustad, R.A., (2012) Creating Performance Curves for Variable Refrigerant Flow Heat Pumps in EnergyPlus
# Cooling Mode
class VariableRefrigerantFlowEP:
    def __init__(self, rated_capacity=31.6548, rated_input_power=9.73, length=10, height=5):

        self.rated_capacity = rated_capacity  # kW
        self.rated_input_power = rated_input_power   # kW

        self.plr_min = 0.2    # minimum operating part load ratio (0~0.4)

        self.length = length   # equivalent piping length from outdoor unit to indoor units, m
        self.height = height   # vertical height of the difference between the highest and lowest terminal unit, m
        self.indoor_capacity = 0  # kW
        self.cr = 0  # combination ratio = (rated part load ratio)

        # datasets for regression analysis
        boundary = pd.read_excel('equipment_spec.xlsx', sheet_name='boundary_dataset', header=None)
        boundary = boundary.drop(boundary.index[0])
        self.boundary = pd.DataFrame(boundary, dtype='float64')

        low_temp_c = pd.read_excel('equipment_spec.xlsx', sheet_name='lowt_dataset_c', header=None)
        low_temp_c = low_temp_c.drop(low_temp_c.index[0])
        self.low_temp_c = pd.DataFrame(low_temp_c, dtype='float64')

        low_temp_p = pd.read_excel('equipment_spec.xlsx', sheet_name='lowt_dataset_p', header=None)
        low_temp_p = low_temp_p.drop(low_temp_p.index[0])
        self.low_temp_p = pd.DataFrame(low_temp_p, dtype='float64')

        high_temp_c = pd.read_excel('equipment_spec.xlsx', sheet_name='hight_dataset_c', header=None)
        high_temp_c = high_temp_c.drop(high_temp_c.index[0])
        self.high_temp_c = pd.DataFrame(high_temp_c, dtype='float64')

        high_temp_p = pd.read_excel('equipment_spec.xlsx', sheet_name='hight_dataset_p', header=None)
        high_temp_p = high_temp_p.drop(high_temp_p.index[0])
        self.high_temp_p = pd.DataFrame(high_temp_p, dtype='float64')

    # combination ratio correction factor
    def get_cr_correction(self):
        cr_data = pd.read_excel('equipment_spec.xlsx', sheet_name='cr_correction', header=None)
        cr_data = cr_data.drop(cr_data.index[0])
        cr_data = pd.DataFrame(cr_data, dtype='float64')

        x_data = np.array(cr_data.iloc[:, 1]).reshape(-1, 1)
        y_data = np.array(cr_data.iloc[:, 0]).reshape(-1, 1)
        model = LinearRegression()
        model.fit(x_data, y_data)
        a = model.coef_
        b = model.intercept_
        cr_correction_factor = a * self.cr + b
        cr_correction_factor = cr_correction_factor[0][0]

        if cr_correction_factor <= 1:
            return 1
        else:
            return cr_correction_factor

    # energy input ratio modifier function of part-load ratio
    def get_eirfplr(self):

        if self.cr <= 1:
            eirfplr_data = pd.read_excel('equipment_spec.xlsx', sheet_name='eirfplr', header=None)
            eirfplr_data = eirfplr_data.drop(eirfplr_data.index[0])
            eirfplr_data = eirfplr_data.dropna(how='all', axis=1)
            eirfplr_data = pd.DataFrame(eirfplr_data, dtype='float64')

            x_data = eirfplr_data.iloc[:, 3:]
            y_data = eirfplr_data.iloc[:, 1]
            model = LinearRegression()
            model.fit(x_data, y_data)
            a, b, c = model.coef_
            d = model.intercept_
            eirfplr = a * self.cr + b * self.cr ** 2 + c * self.cr ** 3 + d

            return eirfplr

    # piping correction factor for length and height
    def get_piping_correction(self):
        pipe_data = pd.read_excel('equipment_spec.xlsx', sheet_name='piping_correction', header=None)
        pipe_data = pipe_data.drop(pipe_data.index[0])
        pipe_data = pd.DataFrame(pipe_data, dtype='float64')

        x_data = pipe_data.iloc[:, 1:]
        y_data = pipe_data.iloc[:, 0]
        model = LinearRegression()
        model.fit(x_data, y_data)
        a = model.intercept_
        b, c, d, e, f = model.coef_
        piping_correction_length = a + b * self.length + c * self.length ** 2 + d * self.cr + e * self.cr ** 2 \
                                   + f * self.length * self.cr

        piping_correction_height = 1 - 0.0019231 * self.height

        return piping_correction_length, piping_correction_height

    # calculation in the condition that pipe loss is considered
    def cal_loss(self, iwb, odb, indoor_capacity):
        self.indoor_capacity = indoor_capacity
        self.cr = self.indoor_capacity / self.rated_capacity
        if self.cr > 1.5:
            self.cr = 1.5
        capacity, input_power, cop = self.cal(iwb, odb)
        piping_correction_length, piping_correction_height = self.get_piping_correction()
        # available capacity of the outdoor unit
        capacity_a = capacity * piping_correction_length * piping_correction_height

        if self.cr == 1:
            cop = capacity_a / input_power
            return capacity_a, input_power, cop

        else:
            cr_correction_factor = self.get_cr_correction()
            eirfplr = self.get_eirfplr()
            # plr: operating part load ratio
            plr = self.indoor_capacity / capacity_a
            cr_limit = self.plr_min * capacity_a / self.rated_capacity

            if self.cr > 1:
                capacity_h = capacity_a * cr_correction_factor
                cop = capacity_h / input_power

                return capacity_h, input_power, cop

            if cr_limit <= self.cr < 1:
                input_power_l = input_power * eirfplr
                capacity_l = self.indoor_capacity
                if self.indoor_capacity > capacity_a:  # when cr is near to 1, like 0.9, this situation may happen
                    capacity_l = capacity_a
                cop = capacity_l / input_power_l

                return capacity_l, input_power_l, cop

            if 0 < self.cr < cr_limit:  # same to plr < plr_min
                cycling_ratio = plr / self.plr_min
                cycling_ratio_fraction = 0.15 * cycling_ratio + 0.85
                rtf = cycling_ratio / cycling_ratio_fraction  # runtime fraction

                input_power_min = input_power * eirfplr * rtf
                capacity_min = self.indoor_capacity
                cop = capacity_min / input_power_min

                return capacity_min, input_power_min, cop

    # calculation in the condition of "cr≠1", i.e. "indoor_capacity"≠"rated_capacity"
    def cal_pl(self, iwb, odb, indoor_capacity):
        self.indoor_capacity = indoor_capacity
        self.cr = self.indoor_capacity / self.rated_capacity
        if self.cr > 1.5:
            self.cr = 1.5   # maximum value of cr
        capacity, input_power, cop = self.cal(iwb, odb)   # the capacity calculated here is the available capacity
        cr_correction_factor = self.get_cr_correction()
        eirfplr = self.get_eirfplr()
        plr = self.indoor_capacity / capacity   # operating part load ratio
        # because "self.cr=indoor_capacity/rated_capacity", plr=rated_capacity/capacity * self.cr
        # i.e. self.cr = plr * capacity/rated_capacity
        cr_limit = self.plr_min * capacity / self.rated_capacity     # get from the relationship between "plr" and "cr"

        if self.cr >= 1:
            capacity_h = capacity * cr_correction_factor
            cop = capacity_h / input_power

            return capacity_h, input_power, cop

        if cr_limit <= self.cr < 1:
            input_power_l = input_power * eirfplr
            capacity_l = self.indoor_capacity
            if self.indoor_capacity > capacity:   # when cr is near to 1, like 0.9, this situation may happen
                capacity_l = capacity
            cop = capacity_l / input_power_l

            return capacity_l, input_power_l, cop

        if 0 < self.cr < cr_limit:   # same to plr < plr_min
            cycling_ratio = plr / self.plr_min
            cycling_ratio_fraction = 0.15 * cycling_ratio + 0.85
            rtf = cycling_ratio / cycling_ratio_fraction  # runtime fraction

            input_power_min = input_power * eirfplr * rtf
            capacity_min = self.indoor_capacity
            cop = capacity_min / input_power_min

            return capacity_min, input_power_min, cop

    # calculation in the condition of "cr=1"
    def cal(self, iwb, odb):
        # regression analysis for Cooling Capacity Ratio Boundary performance curve
        x_data_b = self.boundary.iloc[:, 1:]
        y_data_b = self.boundary.iloc[:, 0]
        model_b = LinearRegression()
        model_b.fit(x_data_b, y_data_b)
        a = model_b.intercept_
        b, c = model_b.coef_
        odb_boundary = a + b * iwb + c * iwb ** 2

        # If the input outdoor dry-bulb temperature is lower than the calculated 'odb_boundary'
        # the low temperature region performance curve is used
        # else the high temperature region performance curve is used
        if odb <= odb_boundary:
            # regression analysis for Cooling Capacity Ratio Modifier Function of Low Temperatures
            x_data_c = self.low_temp_c.iloc[:, 1:]
            y_data_c = self.low_temp_c.iloc[:, 0]
            model_c = LinearRegression()
            model_c.fit(x_data_c, y_data_c)
            intercept_c = model_c.intercept_
            coef_c = model_c.coef_
            capft = intercept_c + coef_c[0] * iwb + coef_c[1] * iwb ** 2 \
                    + coef_c[2] * odb + coef_c[3] * odb ** 2 + coef_c[4] * iwb * odb

            capacity = self.rated_capacity * capft

            # regression analysis for Input Power Ratio Modifier Function of Low Temperatures
            x_data_p = self.low_temp_p.iloc[:, 3:]
            y_data_p = self.low_temp_p.iloc[:, 2]
            model_p = LinearRegression()
            model_p.fit(x_data_p, y_data_p)
            intercept_p = model_p.intercept_
            coef_p = model_p.coef_
            eirft = intercept_p + coef_p[0] * iwb + coef_p[1] * iwb ** 2 \
                    + coef_p[2] * odb + coef_p[3] * odb ** 2 + coef_p[4] * iwb * odb
            power_ratio = eirft * capft

            input_power = self.rated_input_power * power_ratio
            cop = capacity / input_power

            return capacity, input_power, cop

        else:
            # regression analysis for Cooling Capacity Ratio Modifier Function of High Temperatures
            x_data_c = self.high_temp_c.iloc[:, 1:]
            y_data_c = self.high_temp_c.iloc[:, 0]
            model_c = LinearRegression()
            model_c.fit(x_data_c, y_data_c)
            intercept_c = model_c.intercept_
            coef_c = model_c.coef_
            capft = intercept_c + coef_c[0] * iwb + coef_c[1] * iwb ** 2 \
                    + coef_c[2] * odb + coef_c[3] * odb ** 2 + coef_c[4] * iwb * odb

            capacity = self.rated_capacity * capft

            # regression analysis for Input Power Ratio Modifier Function of High Temperatures
            x_data_p = self.high_temp_p.iloc[:, 3:]
            y_data_p = self.high_temp_p.iloc[:, 2]
            model_p = LinearRegression()
            model_p.fit(x_data_p, y_data_p)
            intercept_p = model_p.intercept_
            coef_p = model_p.coef_
            eirft = intercept_p + coef_p[0] * iwb + coef_p[1] * iwb ** 2 \
                    + coef_p[2] * odb + coef_p[3] * odb ** 2 + coef_p[4] * iwb * odb
            power_ratio = eirft * capft

            input_power = self.rated_input_power * power_ratio
            cop = capacity / input_power

            return capacity, input_power, cop
        
        
# HeatingMode
class VRFEPHeatingMode:
    def __init__(self, rated_capacity=37.5, rated_input_power=10.59, length=10, height=5):

        self.rated_capacity = rated_capacity  # kW
        self.rated_input_power = rated_input_power   # kW

        self.indoor_capacity = 0
        self.cr = 0   # combination ratio
        self.plr_min = 0.2    # minimum part load ratio

        self.length = length   # equivalent piping length from outdoor unit to indoor units, m
        self.height = height   # vertical height of the difference between the highest and lowest terminal unit, m

        # dataset for regression analysis
        boundary_c = pd.read_excel('equipment_spec.xlsx', sheet_name='boundary_dataset_c', header=None)
        boundary_c = boundary_c.drop(boundary_c.index[0])
        self.boundary_c = pd.DataFrame(boundary_c, dtype='float64')

        boundary_p = pd.read_excel('equipment_spec.xlsx', sheet_name='boundary_dataset_p', header=None)
        boundary_p = boundary_p.drop(boundary_p.index[0])
        self.boundary_p = pd.DataFrame(boundary_p, dtype='float64')

        low_temp_c = pd.read_excel('equipment_spec.xlsx', sheet_name='lowt_dataset_c_h', header=None)
        low_temp_c = low_temp_c.drop(low_temp_c.index[0])
        self.low_temp_c = pd.DataFrame(low_temp_c, dtype='float64')

        low_temp_p = pd.read_excel('equipment_spec.xlsx', sheet_name='lowt_dataset_p_h', header=None)
        low_temp_p = low_temp_p.drop(low_temp_p.index[0])
        self.low_temp_p = pd.DataFrame(low_temp_p, dtype='float64')

        high_temp_c = pd.read_excel('equipment_spec.xlsx', sheet_name='hight_dataset_c_h', header=None)
        high_temp_c = high_temp_c.drop(high_temp_c.index[0])
        self.high_temp_c = pd.DataFrame(high_temp_c, dtype='float64')

        high_temp_p = pd.read_excel('equipment_spec.xlsx', sheet_name='hight_dataset_p_h', header=None)
        high_temp_p = high_temp_p.drop(high_temp_p.index[0])
        self.high_temp_p = pd.DataFrame(high_temp_p, dtype='float64')

    # combination ratio correction factor
    def get_cr_correction(self):
        cr_data = pd.read_excel('equipment_spec.xlsx', sheet_name='cr_correction_h', header=None)
        cr_data = cr_data.drop(cr_data.index[0])
        cr_data = pd.DataFrame(cr_data, dtype='float64')

        x_data = cr_data.iloc[:, 1:]
        y_data = cr_data.iloc[:, 0]
        model = LinearRegression()
        model.fit(x_data, y_data)
        a = model.intercept_
        b, c, d = model.coef_
        cr_correction_factor = a + b * self.cr + c * self.cr ** 2 + d * self.cr ** 3

        if cr_correction_factor <= 1:
            return 1
        else:
            return cr_correction_factor

    # energy input ratio modifier function of part-load ratio
    def get_eirfplr(self):

        if self.cr <= 1:
            eirfplr_l = pd.read_excel('equipment_spec.xlsx', sheet_name='eirfplr_l', header=None)
            eirfplr_l = eirfplr_l.drop(eirfplr_l.index[0])
            eirfplr_l = eirfplr_l.dropna(how='all', axis=1)
            eirfplr_l = pd.DataFrame(eirfplr_l, dtype='float64')

            x_data = eirfplr_l.iloc[:, 3:]
            y_data = eirfplr_l.iloc[:, 1]
            model = LinearRegression()
            model.fit(x_data, y_data)
            a = model.intercept_
            b, c, d = model.coef_
            eirfplr = a + b * self.cr + c * self.cr ** 2 + d * self.cr ** 3

            return eirfplr

        if self.cr > 1:
            eirfplr_h = pd.read_excel('equipment_spec.xlsx', sheet_name='eirfplr_h', header=None)
            eirfplr_h = eirfplr_h.drop(eirfplr_h.index[0])
            eirfplr_h = eirfplr_h.dropna(how='all', axis=1)
            eirfplr_h = pd.DataFrame(eirfplr_h, dtype='float64')

            x_data = eirfplr_h.iloc[:, 3:]
            y_data = eirfplr_h.iloc[:, 1]
            model = LinearRegression()
            model.fit(x_data, y_data)
            a, b, c = model.coef_
            d = model.intercept_
            eirfplr = a + b * self.cr + c * self.cr ** 2 + d * self.cr ** 3

            return eirfplr

    # piping correction factor for length and height
    def get_piping_correction(self):
        pipe_data = pd.read_excel('equipment_spec.xlsx', sheet_name='piping_correction_h', header=None)
        pipe_data = pipe_data.drop(pipe_data.index[0])
        pipe_data = pd.DataFrame(pipe_data, dtype='float64')

        x_data = pipe_data.iloc[:, 1:]
        y_data = pipe_data.iloc[:, 0]
        model = LinearRegression()
        model.fit(x_data, y_data)
        a = model.intercept_
        b, c, d = model.coef_
        piping_correction_length = a + b * self.length + c * self.length ** 2 + d * self.length ** 3

        piping_correction_height = 0

        piping_correction = piping_correction_length + piping_correction_height

        return piping_correction

    def get_defrost_correction(self, owb):
        # available range of outdoor wet bulb temperature
        if owb < -10:
            owb = -10
        if owb > 5.84:
            owb = 5.84

        df_data = pd.read_excel('equipment_spec.xlsx', sheet_name='df_correction', header=None)
        df_data = df_data.drop(df_data.index[0])
        df_data = pd.DataFrame(df_data, dtype='float64')

        x_data = df_data.iloc[:, 1:]
        y_data = df_data.iloc[:, 0]
        model = LinearRegression()
        model.fit(x_data, y_data)
        a = model.intercept_
        b, c, d = model.coef_
        defrost_correction = a + b * owb + c * owb ** 2 + d * owb ** 3

        return defrost_correction

    # calculation in the condition that pipe loss and defrost correction is considered
    def cal_loss(self, idb, owb, indoor_capacity):
        self.indoor_capacity = indoor_capacity
        self.cr = self.indoor_capacity / self.rated_capacity
        if self.cr > 1.5:
            self.cr = 1.5
        piping_correction = self.get_piping_correction()
        defrost_correction = self.get_defrost_correction(owb=owb)

        capacity, input_power, cop = self.cal(idb, owb)
        capacity_a = capacity * defrost_correction * piping_correction

        if self.cr == 1:
            cop = capacity_a / input_power

            return capacity_a, input_power, cop
        else:
            cr_correction_factor = self.get_cr_correction()
            eirfplr = self.get_eirfplr()
            plr = self.indoor_capacity / capacity_a
            cr_limit = self.plr_min * capacity_a / self.rated_capacity

            if self.cr > 1:
                capacity_h = capacity_a * cr_correction_factor
                cop = capacity_h / input_power

                return capacity_h, input_power, cop

            if cr_limit <= self.cr < 1:
                input_power_l = input_power * eirfplr
                capacity_l = self.indoor_capacity
                if self.indoor_capacity > capacity_a:  # when cr is near to 1, like 0.9, this situation may happen
                    capacity_l = capacity_a
                cop = capacity_l / input_power_l

                return capacity_l, input_power_l, cop

            if 0 < self.cr < cr_limit:  # same to plr < plr_min
                cycling_ratio = plr / self.plr_min
                cycling_ratio_fraction = 0.15 * cycling_ratio + 0.85
                rtf = cycling_ratio / cycling_ratio_fraction  # runtime fraction

                input_power_min = input_power * eirfplr * rtf
                capacity_min = self.indoor_capacity
                cop = capacity_min / input_power_min

                return capacity_min, input_power_min, cop

    # calculation in the condition of "cr≠1", i.e. in an instance, "rated_indoor_capacity" ≠ "rated_capacity"
    def cal_pl(self, idb, owb, indoor_capacity):
        self.indoor_capacity = indoor_capacity
        self.cr = self.indoor_capacity / self.rated_capacity
        if self.cr > 1.5:
            self.cr = 1.5
        capacity, input_power, cop = self.cal(idb, owb)
        cr_correction_factor = self.get_cr_correction()
        eirfplr = self.get_eirfplr()
        plr = self.indoor_capacity / capacity
        cr_limit = self.plr_min * capacity / self.rated_capacity

        if self.cr >= 1:
            capacity_h = capacity * cr_correction_factor
            cop = capacity_h / input_power

            return capacity_h, input_power, cop

        if cr_limit <= self.cr < 1:
            input_power_l = input_power * eirfplr
            capacity_l = self.indoor_capacity
            if self.indoor_capacity > capacity:   # when cr is near to 1, like 0.9, this situation may happen
                capacity_l = capacity
            cop = capacity_l / input_power_l

            return capacity_l, input_power_l, cop

        if 0 < self.cr < cr_limit:
            cycling_ratio = plr / self.plr_min
            cycling_ratio_fraction = 0.15 * cycling_ratio + 0.85
            rtf = cycling_ratio / cycling_ratio_fraction  # runtime fraction

            input_power_min = input_power * eirfplr * rtf
            capacity_min = self.indoor_capacity
            cop = capacity_min / input_power_min

            return capacity_min, input_power_min, cop

    # calculation in the condition of "cr==1"
    def cal(self, idb, owb):
        # regression analysis for Heating Capacity Ratio Boundary performance curve
        x_data_c = self.boundary_c.iloc[:, 1:]
        y_data_c = self.boundary_c.iloc[:, 0]
        model = LinearRegression()
        model.fit(x_data_c, y_data_c)
        ac = model.intercept_
        bc, cc = model.coef_
        boundary_c = ac + bc * idb + cc * idb ** 2

        # regression analysis for Heating Input Power Boundary performance curve
        x_data_p = self.boundary_p.iloc[:, 1:]
        y_data_p = self.boundary_p.iloc[:, 0]
        model = LinearRegression()
        model.fit(x_data_p, y_data_p)
        ap = model.intercept_
        bp, cp = model.coef_
        boundary_p = ap + bp * idb + cp * idb ** 2

        # regression analysis for Heating Capacity Ratio Modifier Function of Low Temperatures
        x_data_c_l = self.low_temp_c.iloc[:, 1:]
        y_data_c_l = self.low_temp_c.iloc[:, 0]
        model_c = LinearRegression()
        model_c.fit(x_data_c_l, y_data_c_l)
        al = model_c.intercept_
        bl, cl, dl, el, fl = model_c.coef_
        capft_l = al + bl * idb + cl * idb ** 2 + dl * owb + el * owb ** 2 + fl * idb * owb

        # regression analysis for Heating Capacity Ratio Modifier Function of High Temperatures
        x_data_c_h = self.high_temp_c.iloc[:, 1:]
        y_data_c_h = self.high_temp_c.iloc[:, 0]
        model_c_h = LinearRegression()
        model_c_h.fit(x_data_c_h, y_data_c_h)
        ah = model_c_h.intercept_
        bh, ch, dh, eh, fh = model_c_h.coef_
        capft_h = ah + bh * idb + ch * idb ** 2 + dh * owb + eh * owb ** 2 + fh * idb * owb

        # regression analysis for Input Power Ratio Modifier Function of Low Temperatures
        x_data_p_l = self.low_temp_p.iloc[:, 3:]
        y_data_p_l = self.low_temp_p.iloc[:, 2]
        model_p_l = LinearRegression()
        model_p_l.fit(x_data_p_l, y_data_p_l)
        gl = model_p_l.intercept_
        hl, il, jl, kl, ll = model_p_l.coef_
        eirft_l = gl + hl * idb + il * idb ** 2 + jl * owb + kl * owb ** 2 + ll * idb * owb

        # regression analysis for Input Power Ratio Modifier Function of High Temperatures
        x_data_p_h = self.high_temp_p.iloc[:, 3:]
        y_data_p_h = self.high_temp_p.iloc[:, 2]
        model_p_h = LinearRegression()
        model_p_h.fit(x_data_p_h, y_data_p_h)
        gh = model_p_h.intercept_
        hh, ih, jh, kh, lh = model_p_h.coef_
        eirft_h = gh + hh * idb + ih * idb ** 2 + jh * owb + kh * owb ** 2 + lh * idb * owb

        # If the input outdoor wet-bulb temperature is lower than the calculated boundary owb
        # the low temperature region performance curve is used,
        # else the high temperature region performance curve is used.
        if owb <= boundary_c and owb <= boundary_p:
            capacity = self.rated_capacity * capft_l
            power_ratio = eirft_l * capft_l
            input_power = self.rated_input_power * power_ratio
            cop = capacity / input_power

            return capacity, input_power, cop

        if owb > boundary_c and owb > boundary_p:
            capacity = self.rated_capacity * capft_h
            power_ratio = eirft_h * capft_h
            input_power = self.rated_input_power * power_ratio
            cop = capacity / input_power

            return capacity, input_power, cop

        if boundary_c > owb > boundary_p:
            capacity = self.rated_capacity * capft_l
            power_ratio = eirft_h * capft_l
            input_power = self.rated_input_power * power_ratio
            cop = capacity / input_power

            return capacity, input_power, cop

        if boundary_c < owb < boundary_p:
            capacity = self.rated_capacity * capft_h
            power_ratio = eirft_l * capft_h
            input_power = self.rated_input_power * power_ratio
            cop = capacity / input_power

            return capacity, input_power, cop
        
        
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
                # print(Twbout0)
                # 出口空気は飽和空気という仮定で、出口空気の比エンタルピーを求める。
                [hout, xout] = tdb_rh2h_x(Twbout0,100)
                
                # 空気平均比熱cpeの計算
                dh = (hout - hin)*1000 # 比エンタルピーの単位をJ/kgに！
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
                # print(Q,Twbout)
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
    

# 蓄熱槽
class TES():
    def water_density(self, temp):
        # https://www.sit.ac.jp/user/konishi/JPN/Lecture/ThermalFluid/ThermalFluid_1stAll.pdf
        # temp ℃
        # density kg/m^3
        return (999.83952 + 16.945176 * temp - 7.987041 * 10e-3 * temp ** 2 - 46.170461 * 10e-6 * temp ** 3 + 105.56302 * 10e-9 * temp ** 4 - 280.54253 * 10e-12 * temp ** 5) /  (1 + 16.879850 * 10e-3 * temp)

    def water_thermal_conductivity(self, temp):
        # 水の伝導率　W/(m*K)
        a = [-1.3734399e-1, 4.2128755, -5.9412196, 1.2794890]
        temp_critical_point = 647.096
        temp_k = temp + 273.15
        tr = (temp_critical_point - temp_k) / temp_critical_point

        lamb = a[len(a) - 1]
        for i in range(len(a) - 2, 0, -1):
            lamb = a[i] + lamb * tr
        return lamb

    def water_specific_heat(self, temp):
        # kJ/(kg*K)
        a = [1.0570130, 2.1952960e1, -4.9895501e1, 3.6963413e1]
        temp_critical_point = 647.096
        temp_k = temp + 273.15
        tr = (temp_critical_point - temp_k) / temp_critical_point

        cpw = a[len(a) -1]
        for i in range(len(a) - 2, 0, -1):
            cpw = a[i] + cpw * tr
        return cpw

    def water_thermal_diffusivity(self, temp):
        # 水の熱拡散率　m^2/s
        lamb = self.water_thermal_conductivity(temp)
        cp = self.water_specific_heat(temp)
        rho = self.water_density(temp)
        return lamb / (1000 * cp * rho)

    def TDMA_solver(self, a, b, c, d):
        nf = len(d)
        ac, bc, cc, dc = map(np.array, (a, b, c, d))
        for it in range(1, nf):
            mc = ac[it - 1] / bc[it - 1]
            bc[it] = bc[it] - mc * cc[it - 1]
            dc[it] = dc[it] - mc * dc[it - 1]
        xc = bc
        xc[-1] = dc[-1] / bc[-1]

        for il in range(nf-2, -1, -1):
            xc[il] = (dc[il] - cc[il] * xc[il + 1]) / bc[il]

        return xc

    def __init__(self, dt):
        # 0：蓄熱槽上部
        # XXX：蓄熱槽下部
        self.pipeinstal_height = 2.8  # 設置高さm
        self.d_in = 0.1#0.5  # 流出入口円管直径 m
        self.l_deepth = 3  # 水槽深さ m
        self.area_section = 4 * 4  # 断面積 m
        self.timestep = dt  # sec
        self.temp_water_inlet = 7  # 送水温度
        self.flowrate_water = 15/3600  # 送水流量 m^3/s
        self.heatloss_coef = 0.001 * 4.8 ** 2 * 6 * 0.04 / 0.4  # 熱損失率kw/k  0.04 W/(m*K)  100mm
        self.temp_ambient = 25  # 周囲温度
        self.sig_downflow = 0  # 下向き:1　上向き:0　信号
        self.num_layer = 250  # 分割数

        # 計算行列式
        self.cal_mat = np.array([[0]*self.num_layer]*3, dtype=float)
        self.vec1 = np.array([0]*self.num_layer, dtype=float)
        self.vec2 = np.array([0]*self.num_layer, dtype=float)

        self. dz = self.l_deepth / self.num_layer  # 分割幅
        self.pipeinstal_layer = int(self.pipeinstal_height / self.dz)  # 流入口設置層番号　（下部）
        self.temp_reference = 15  # 基準温度は冷凍機の入口温度と同じとする
        self.tes_temp = np.array([self.temp_reference]*self.num_layer, dtype=float)

        # self.tes_temp_p = np.array([12]*self.num_layer, dtype=float)
        #print(self.heat_cal())


    def tes_cal(self, temp_water_inlet=7, flowrate_water=15/3600, sig_downflow=0, temp_ambient=25):
        self.temp_water_inlet = temp_water_inlet
        self.flowrate_water = flowrate_water
        self.sig_downflow = sig_downflow
        self.temp_ambient = temp_ambient
        self.temp_avg = sum(self.tes_temp) / self.num_layer  # 蓄熱槽平均温度
        # 混合域の噴流配分計算
        if self.flowrate_water == 0:
            # 流量がない場合、熱拡散と外部への熱損失のみ
            self.cal_mat = np.array([[0] * self.num_layer] * 3, dtype=float)
            self.vec1 = np.array([0] * self.num_layer, dtype=float)
            self.vec2 = np.array([0] * self.num_layer, dtype=float)

        elif (self.sig_downflow and self.temp_water_inlet <= self.tes_temp[0]) or (not self.sig_downflow and self.tes_temp[self.num_layer - 1] <= self.temp_water_inlet):
            # 下部から温水が流入と上部から冷水が流入の場合、水の密度が逆転するため、逆転の続く層までが完全混合になるとする
            # 平均温度を計算
            if self.sig_downflow:
                temp_mixavg = self.tes_temp[0]
                temp_mix = self.tes_temp[0] + self.timestep / (self.area_section * self.dz) * (self.temp_water_inlet - self.tes_temp[0]) * self.flowrate_water
            else:
                temp_mixavg = self.tes_temp[len(self.tes_temp) - 1]
                temp_mix = self.tes_temp[len(self.tes_temp) - 1] + self.timestep / (self.area_section * self.dz) * (self.temp_water_inlet - self.tes_temp[len(self.tes_temp) - 1])

            for num_mixed in range(1, self.num_layer):
                if self.sig_downflow:
                    if self.tes_temp[num_mixed] < temp_mix:
                        break
                    temp_mix = (temp_mix * num_mixed + self.tes_temp[num_mixed]) / (num_mixed + 1)
                    temp_mixavg += self.tes_temp[num_mixed]
                else:
                    tgtlayer = self.num_layer - (num_mixed + 1)
                    if temp_mixavg < self.tes_temp[tgtlayer]:
                        break
                    temp_mix = 0.5 * (temp_mix + self.tes_temp[tgtlayer])
                    temp_mixavg += self.tes_temp[tgtlayer]

            temp_mixavg /= num_mixed
            bf = self.flowrate_water / (num_mixed * self.dz)

            # 平均温度と噴流配分
            for i in range(0, self.num_layer):
                tgtlayer = i
                # 上向き
                if not self.sig_downflow:
                    tgtlayer = self.num_layer - (i + 1)

                if i < num_mixed:
                    self.vec1[tgtlayer] = bf
                    self.tes_temp[tgtlayer] = temp_mixavg
                    self.vec2[tgtlayer] = self.dz / self.area_section * self.vec1[tgtlayer]
                else:
                    self.vec1[tgtlayer] = 0
                    self.vec2[tgtlayer] = 0

                if i != 0:
                    if self.sig_downflow:
                        self.vec2[tgtlayer] += self.vec2[tgtlayer - 1]
                    else:
                        self.vec2[tgtlayer] += self.vec2[tgtlayer + 1]
        else:
            area_pipe = math.pow(self.d_in / 2, 2) * math.pi  # 流入断面積 m^2
            u_waterin2 = math.pow(self.flowrate_water / area_pipe, 2)  # 流入速度2乗 (m/s)^2
            rho = self.water_density(self.temp_water_inlet)

            # 噴流が到達する層を求める
            tgt = rho * u_waterin2 / (9.8 * self.dz)  # 到達層の密度
            rr = 0
            for lmax in range(0, self.num_layer - 1):
                if self.sig_downflow:
                    rr += (self.water_density(self.tes_temp[lmax]) - rho)  # 密度差を積算
                else:
                    rr += (rho - self.water_density(self.tes_temp[self.num_layer - lmax - 1]))
                if rr > tgt:
                    break
            if not self.sig_downflow:
                lmax = self.num_layer - lmax - 1

            # 混合域深さの計算
            temp_lmax = self.tes_temp[lmax]
            if temp_lmax == self.temp_water_inlet:
                # 到達層の温度が流入温度と同じの場合、混合域を100％とする
                lm = self.l_deepth
            else:
                rho0 = self.water_density(temp_lmax)
                self.ar = self.d_in * 9.8 * abs(rho0 - rho) / (rho0 * u_waterin2)  # アルキメデス数

                ndt = 0 # 無次元時間
                if self.sig_downflow:
                    for i in range(0, lmax):
                        ndt += (self.tes_temp[i] - temp_lmax)
                else:
                    for i in range(lmax, self.num_layer):
                        ndt += (self.tes_temp[i] - temp_lmax)
                ndt = (ndt * self.dz) / (self.l_deepth * (self.temp_water_inlet - temp_lmax))
                lm = self.l_deepth * 0.8 * math.pow(self.ar, -0.5) * self.d_in / self.l_deepth + 0.5 * ndt  # 混合域深さ

            z1 = 0
            bf = self.flowrate_water / (2 * lm ** 3)
            for i in range(0, self.num_layer):
                ln = i
                if not self.sig_downflow:
                    ln = self.num_layer - (i + 1)
                z2 = z1 + self.dz
                # vec1 第ｌｎ層の鉛直方向単位長さあたりの平均的な流入水量{m^2/s]
                if z2 < lm:
                    self.vec1[ln] = bf * (3 * lm ** 2 - self.dz ** 2 * (3 * i * (i + 1) + 1))
                elif lm < z1:
                    self.vec1[ln] = 0
                else:
                    self.vec1[ln] = bf * math.pow(i * self.dz - lm, 2) * (i + 2 * lm / self.dz)

                # vec2 第ｌｎ層の垂直方向の水速Uｍ　積算流入水量を用いて計算する
                if i == 0:
                    self.vec2[ln] = self.dz / self.area_section * self.vec1[ln]
                elif self.sig_downflow:
                    self.vec2[ln] = self.vec2[ln - 1] + self.dz / self.area_section * self.vec1[ln]
                else:
                    self.vec2[ln] = self.vec2[ln + 1] + self.dz / self.area_section * self.vec1[ln]
                z1 = z2

        # 行列式を解く
        outlet_layer = self.pipeinstal_layer   # 3.8/(4/500)
        if not self.sig_downflow:
            #　上向きの場合、流出口が上にある、流入口が下にある
            outlet_layer = self.num_layer - self.pipeinstal_layer - 1

        s = self.timestep * self.water_thermal_diffusivity(self.temp_avg) / (self.dz ** 2)
        p = self.heatloss_coef * self.timestep / (self.water_density(self.temp_avg) * 4.186 * self.l_deepth * self.area_section)

        for i in range(0, self.num_layer):
            r1 = 0
            r2 = 0
            if self.sig_downflow and i != 0 and i <= outlet_layer:
                r1 = self.vec2[i - 1] * self.timestep / self.dz
            if not self.sig_downflow and i != self.num_layer - 1 and i >= outlet_layer:
                r2 = self.vec2[i + 1] * self.timestep / self.dz

            if i == self.num_layer - 1:
                self.cal_mat[0, i] = -(2 * s + r1)
            elif i != 0:
                self.cal_mat[0, i] = -(s + r1)

            if i == 0:
                self.cal_mat[2, i] = -(2 * s + r2)
            elif i != self.num_layer - 1:
                self.cal_mat[2, i] = -(s + r2)

            self.cal_mat[1, i] = 2 * s + r1 + r2 + 1 + p
            self.tes_temp[i] += p * self.temp_ambient

            if self.vec1[i] != 0:
                q = self.timestep * self.vec1[i] / self.area_section
                self.cal_mat[1, i] += q
                self.tes_temp[i] += q * self.temp_water_inlet
        # aa = cal_mat[0, 1:num_layer]
        # cc = cal_mat[2, 0:num_layer-1]
        self.tes_temp_out_p = self.tes_temp[outlet_layer]
        self.tes_temp = self.TDMA_solver(self.cal_mat[0, 1:self.num_layer], self.cal_mat[1, :], self.cal_mat[2, 0:self.num_layer-1], self.tes_temp)
        self.tes_temp_out = self.tes_temp[outlet_layer]

    def heat_cal(self):
        # 蓄熱量　MJ
        #　蓄熱がプラス　蓄冷がマイナス
        sum = 0
        for i in range(0, len(self.tes_temp)):
            sum += (self.tes_temp[i] - self.temp_reference)
        rho_ref = self.water_density(self.temp_reference)
        return 0.001 * sum * rho_ref * 4.186 * self.dz * self.area_section

    
    
# 水・水熱交換器
class Water_to_water():
    def __init__(self):
        self.flowrate_high = 0  # 高温側の流速[m**3/min]
        self.flowrate_low = 0  # 低温側の流速[m**3/min]
        self.t_water_inlet_high = 0  # 高温側の入口温度
        self.t_water_inlet_low = 0  # 低温側の入口温度
        self.t_water_outlet_high = 0  # 高温側の出口温度
        self.t_water_outlet_low = 0  # 低温側の出口温度

    def cal(self, flowrate_high, flowrate_low, t_water_inlet_high, t_water_inlet_low, t_water_outlet_high, t_water_outlet_low):
        # 熱交換率 k [kW/m**2k]
        # ah,ac:高温側、低温側の熱伝導率[kcal/m2h`C]
        # Cp: 流体比熱[kcal / kg `C]
        # gamma: 比重量[kg / m3]
        # L: 流量[kg / h]
        # S: 通過断面積[m2]
        # eta: 粘性係数[kgs / m2]
        # mu: 粘度[kg / mh] = 3600 * 9.80 * eta
        # lambda: 流体の熱伝導率[kcal / mh `C]
        # De = 2cd / (c + d)(c: 通路長[m], d: 通路幅[m])
        # T: 流体の温度
        flowrate_high = flowrate_high / 1000 * 60  # kg/s -> m^3/min
        flowrate_low = flowrate_low / 1000 * 60  # kg/s -> m^3/min
        # print(flowrate_high, flowrate_low)
        # 流量が少なくとも片方ない場合
        if flowrate_high < 0.01 or flowrate_low < 0.01:
            t_water_outlet_high = t_water_inlet_high
            t_water_outlet_low = t_water_inlet_low
        elif flowrate_high < 0.01 and flowrate_low > 0.01:
            t_water_outlet_high = t_water_inlet_high
            t_water_outlet_low = t_water_inlet_low
        elif flowrate_high > 0.01 and flowrate_low < 0.01:
            t_water_outlet_high = t_water_inlet_high
            t_water_outlet_low = t_water_inlet_low
        else:
            # 流量が両方ある場合
            flag = 0
            # 高温側が低温側より低温の場合はデータを入れ替えて計算
            if t_water_inlet_high < t_water_inlet_low:
                flag = 1
                t_temp = t_water_inlet_high
                t_water_inlet_high = t_water_inlet_low
                t_water_inlet_low = t_temp
                flowrate_temp = flowrate_high
                flowrate_high = flowrate_low
                flowrate_low = flowrate_temp

            cp = 1  # Cp:流体比熱[kcal/kg`C]
            # 機器特性
            s = 0.01
            c = 40
            d = 1
            de = 2 * c * d / (c + d)
            area = 250#992.25

            # 変数ah
            # #高温側、低温側の温度は、出入口温度の平均値とする
            t_avg = (t_water_inlet_high + t_water_outlet_high) / 2
            gamma = 1.735 * 10.0 ** (-5.0) * t_avg ** 3.0 - 6.133 * 10.0 ** (-3.0) * t_avg ** 2.0 + 2.704 * 10.0 ** (
                -2.0) * t_avg + 1000.0
            l = flowrate_high * 60 * gamma
            eta = 4.359 * 10.0 ** (-8.0) * t_avg ** 4.0 - 1.109 * 10.0 ** (-5.0) * t_avg ** 3.0 + 1.107 * 10.0 ** (
                -3.0) * t_avg ** 2.0 - 5.824 * 10.0 ** (-2.0) * t_avg + 1.826
            eta = eta * 10.0 ** (- 4.0)
            mu = 3600.0 * 9.80 * eta
            lamb = -5.672 * 10.0 ** (-6.0) * t_avg ** 2.0 + 1.556 * 10.0 ** (-3.0) * t_avg + 0.4894
            ah = 0.023 * cp ** (1.0 / 3.0) * l ** 0.8 * lamb ** (2.0 / 3.0) * s ** (-0.8) * mu ** (
                        -7.0 / 15.0) * de ** (-0.2)

            # whの計算
            # 高温側の流量(kg/s)×比熱(kJ/kgK)
            wh = flowrate_high / 60 * gamma * 4.186

            # ac
            t_avg = (t_water_inlet_low + t_water_outlet_low) / 2
            gamma = 1.735 * 10.0 ** (-5.0) * t_avg ** 3.0 - 6.133 * 10.0 ** (-3.0) * t_avg ** 2.0 + 2.704 * 10.0 ** (
                -2.0) * t_avg + 1000.0
            l = flowrate_low * 60 * gamma
            eta = 4.359 * 10.0 ** (-8.0) * t_avg ** 4.0 - 1.109 * 10.0 ** (-5.0) * t_avg ** 3.0 + 1.107 * 10.0 ** (
                -3.0) * t_avg ** 2.0 - 5.824 * 10.0 ** (-2.0) * t_avg + 1.826
            eta = eta * 10.0 ** (- 4.0)
            mu = 3600.0 * 9.80 * eta
            lamb = -5.672 * 10.0 ** (-6.0) * t_avg ** 2.0 + 1.556 * 10.0 ** (-3.0) * t_avg + 0.4894
            ac = 0.023 * cp ** (1.0 / 3.0) * l ** 0.8 * lamb ** (2.0 / 3.0) * s ** (-0.8) * mu ** (
                        -7.0 / 15.0) * de ** (-0.2)

            # wcの計算
            # 低温側の流量(kg/s)×比熱(kJ/kgK)
            wc = flowrate_low / 60 * gamma * 4.186

            # kの算出 kcal/m2h`C からkW/m2`Cへ変換
            k = ah * ac / (ah + ac)
            k *= 1.162 * 10 ** (-3)

            ka = k * area

            wcwh = wc / wh
            z = ka * (1 - wcwh) / wc

            if wcwh != 1:
                x = math.exp(z)
                y = t_water_inlet_high - t_water_inlet_low
                t_water_outlet_high = t_water_inlet_high - y * (1 - x) / (1 - x / wcwh)
                t_water_outlet_low = t_water_inlet_low + y * (1 - x) / (wcwh - x)

                if z > 200:
                    # 向流型の場合流量が少ない方は十分に熱交換され、
                    # そうでない方は流量に応じた温度変化になる。
                    if wc > wh:
                        t_water_outlet_high = t_water_inlet_low
                        t_water_outlet_low = (t_water_inlet_high - t_water_inlet_low) * wh / wc + t_water_inlet_low
                    else:
                        t_water_outlet_low = t_water_inlet_high
                        t_water_outlet_high = (t_water_inlet_low - t_water_inlet_high) * wh / wc + t_water_inlet_high
            else:
                y = t_water_inlet_high - t_water_inlet_low
                t_water_outlet_high = t_water_inlet_high - y * ka / (wc + ka)
                t_water_outlet_low = t_water_inlet_low - y * ka / (wc + ka)

            # 2次側出口温度は1次側出口温度を、1次側出口温度は2次側入口温度を超えない。
            if t_water_outlet_high < t_water_inlet_low or t_water_outlet_low > t_water_inlet_high:
                # 向流型の場合流量が少ない方は十分に熱交換され、
                # そうでない方は流量に応じた温度変化になる。
                if flowrate_low > flowrate_high:
                    t_water_outlet_high = t_water_inlet_low
                    t_water_outlet_low = (t_water_outlet_high - t_water_inlet_high) * flowrate_high / flowrate_low + t_water_inlet_low
                else:
                    t_water_outlet_low = t_water_inlet_high
                    t_water_outlet_high = (t_water_outlet_low - t_water_inlet_low) * flowrate_low / flowrate_high + t_water_inlet_high
            if flag == 1:
                t_temp = t_water_outlet_high
                t_water_outlet_high = t_water_outlet_low
                t_water_outlet_low = t_temp
                flowrate_temp = flowrate_high
                flowrate_high = flowrate_low
                flowrate_low = flowrate_temp
                
        return flowrate_high, flowrate_low, t_water_inlet_high, t_water_inlet_low, t_water_outlet_high, t_water_outlet_low

    

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
            # p_b intercept
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
    def __init__(self, pg=[0.6467, 0.0082, -0.0004, 0], eg=[-0.0166, 0.0399, -0.0008], r_ef=0.6):
        # pg    :圧力-流量(pg)曲線の係数（切片、一次、二次、三次）
        # eg    :効率-流量(eg)曲線の係数（切片、一次、二次）
        # r_ef  :定格時の最高効率(本来は計算によって求める？)rated efficiency
        # inv   :回転数比(0.0~1.0)
        # dp_f  :ファン揚程[Pa]  # 21/05/21 単位kPaから修正
        # g     :流量[m3/min]
        # pw    :消費電力[kW]
        # flag  :計算に問題があったら1、なかったら0
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

    def f2p(self, g):  # flow to pressure for fan
        self.g = g
        # 流量がある場合のみ揚程を計算する
        if self.g > 0:
            self.dp = (self.pg[0] + self.pg[1] * (self.g / self.inv) + self.pg[2] * (
                    self.g / self.inv) ** 2 + self.pg[3] * (self.g / self.inv) ** 3) * self.inv ** 2
        else:
            self.dp = 0

        if self.dp < 0:
            self.dp = 0
            self.flag = 1
        else:
            self.flag = 0

        return self.dp

    def f2p_co(self):  # coefficient for f2p
        if self.inv > 0:
            co_0 = self.pg[0] * self.inv ** 2
            co_1 = self.pg[1] * self.inv
            co_2 = self.pg[2]
            co_3 = self.pg[3] / self.inv

        else:
            co_0 = 0
            co_1 = 0
            co_2 = 0
            co_3 = 0

        return [co_0, co_1, co_2, co_3]

    def cal(self):
        # 流量がある場合のみ消費電力を計算する
        if self.g > 0 and self.inv > 0:
            # G: INV=1.0時（定格）の流量
            G = self.g / self.inv
            # K: 効率換算係数
            K = (1.0 - (1.0 - self.r_ef) / (self.inv ** 0.2)) / self.r_ef
            # ef: 効率
            self.ef = K * (self.eg[0] + self.eg[1] * G + self.eg[2] * G ** 2)

            self.dp = (self.pg[0] + self.pg[1] * (self.g / self.inv) + self.pg[2] * (
                    self.g / self.inv) ** 2 + self.pg[3] * (self.g / self.inv) ** 3) * self.inv ** 2
            if self.dp < 0:
                self.dp = 0
                self.flag = 1

            #  軸動力を求める
            if self.ef > 0:
                self.pw = self.g * (self.dp / 1000) / (60 * 0.8 * self.ef)  # 0.8は実測値から求めたモーター損失
                self.flag = 0
            else:
                self.pw = 0
                self.flag = 2

        else:
            self.pw = 0.0
            self.flag = 0
 

# 蒸気噴霧式加湿器
class SteamSprayHumidifier:
    # from HVACSIM+ TYPE 22 https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nbsir84-2996.pdf p90
    # from TRNSYS https://sel.me.wisc.edu/trnsys/trnlib/aux_heat_and_cool/616new.for
    def __init__(self, area_humidifier=0.42, dp=45, eff=1.0):
        # 空気の流れに蒸気を注入して空気の湿度を高める定圧プロセスの出口空気温度、流量、絶対湿度を計算
        # 出口空気の絶対湿度は，蒸気流量または飽和絶対湿度（大気圧時）に飽和効率を乗じた値により制限
        
        # 仕様書
        # area_humidifier       加湿器面積[m2]
        # dp:                   圧力損失[Pa]
        # eff:                  飽和効率[-]

        # 入力
        # tdb_air_in:           入口空気乾球温度['C]
        # w_air_in:             入口空気絶対湿度[kg/kg']
        # frowrate_air_in:      入口空気質量流量[kg/s]
        # t_steam_in            入口水蒸気温度[℃]
        # flowrate_steam_in:    入口水蒸気流量[kg/s]

        # 出力
        # tdb_air_out:          出口空気乾球温度['C]
        # w_air_out:            出口空気絶対湿度[kg/kg']
        # flowrate_air_out      出口空気質量流量[kg/s]

        # 内部変数
        # Cpa:                  乾き空気の定圧比熱 [kJ/kg・K]
        # Cps:                  水蒸気の定圧比熱 [kJ/kg・K]
        # Cpai:                 入口水蒸気の定圧比熱 [kJ/kg・K]
        # psat:                 出口空気飽和時の水蒸気分圧[kPa]
        # wsat:                 出口空気飽和時の絶対湿度[kg/kg']

        self.area_humidifier = area_humidifier
        self.dp = dp
        self.eff = eff

        # その都度変わる値
        self.tdb_air_in = 0
        self.w_air_in = 0
        self.flowrate_air_in = 0
        self.flowrate_steam_in = 0
        self.t_steam_in = 0
        self.tdb_air_out = 0
        self.w_air_out = 0
        self.flowrate_air_out = 0

    def cal(self, tdb_air_in, w_air_in, flowrate_air_in, flowrate_steam_in, t_steam_in):
        self.tdb_air_in = tdb_air_in
        self.w_air_in = w_air_in
        self.flowrate_air_in = flowrate_air_in
        self.flowrate_steam_in = flowrate_steam_in
        self.t_steam_in = t_steam_in

        Cpa = 1.006  # 乾き空気の定圧比熱 [kJ/kg・K]
        Cps = 1.86  # 水蒸気の定圧比熱 [kJ/kg・K]
        
        # 入口空気の定圧比熱は入口絶対湿度に依存する
        Cpai = (Cpa + self.w_air_in * Cps) / (1 + self.w_air_in)

        # 出口空気温度は入口空気と水蒸気温度の重み付け平均で求められる
        self.tdb_air_out = (self.flowrate_steam_in * Cps * self.t_steam_in + self.flowrate_air_in * Cpai * self.tdb_air_in) \
                           / (self.flowrate_steam_in * Cps + self.flowrate_air_in * Cpai)
        
        # 噴霧される蒸気のすべてが、空気を加湿したと仮定した際の出口空気の絶対湿度
        w_air_out = self.w_air_in + self.flowrate_steam_in * (1 + self.w_air_in) / self.flowrate_air_in

        # 出口空気が飽和している際の絶対湿度は、飽和空気の水蒸気分圧を用いて計算できる
        p_sat = psy_psat_tsat(self.tdb_air_out)
        w_sat = psy_w_pv(p_sat)

        # 出口空気の絶対湿度は飽和効率と飽和空気の絶対湿度の積を越えることはできない
        self.w_air_out = min(w_air_out, self.eff * w_sat)
        
        # 水分が加わることで空気の質量流量がわずかに増加する
        self.flowrate_air_out = self.flowrate_air_in * (1+self.w_air_out) / (1+self.w_air_in)

        return self.tdb_air_out, self.w_air_out, self.flowrate_air_out

    

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
# 二次方程式の解の公式
def quadratic_formula(co_0, co_1, co_2):
    flag = 0
    if co_1**2 - 4*co_2*co_0 > 0:
        g1 = (-co_1 + (co_1**2 - 4*co_2*co_0)**0.5)/(2 * co_2)
        g2 = (-co_1 - (co_1**2 - 4*co_2*co_0)**0.5)/(2 * co_2)
        if max(g1, g2) < 0:
            g = 0.0
            flag = 1
        else:
            g = max(g1, g2)
    else:
        g = 0.0
        flag = 2
    return [g, flag]

# 並列ポンプ複数台とバイパス弁のユニット（Pumpと同様に取扱可能）
class Pump_para:
    # コンポジションというpython文法を使う
    # def __init__()の中の値はデフォルト値。指定しなければこの値で計算される。
    def __init__(self, pump, num=2, valve=None, kr_pipe_pump=0.0, kr_pipe_valve=0.0):
        # pump          :ポンプオブジェクト。ポンプは1種類のみ指定可能
        # num           :ポンプ台数。1台以上。
        # valve         :弁オブジェクト。バイパス弁。
        # kr_pipe_pump  :ポンプ用管の圧損係数[kPa/(m3/min)^2]
        # kr_pipe_valve :バイパス弁用管の圧損係数[kPa/(m3/min)^2]
        # dp            :ユニットの出入口差圧[kPa]加圧：+, 減圧：-
        # g             :ユニットの出入り流量[m3/min]
        # para          :並列ポンプか否かのフラグ
        self.pump = pump
        self.num = num
        self.valve = valve
        self.kr_pipe_pump = kr_pipe_pump
        self.kr_pipe_valve = kr_pipe_valve
        self.g = 0.0
        self.dp = 0.0
        self.flag = 0
        self.para = 1
        if num < 1:
            print("define at least one pump")

    def f2p(self, g): # 出入口流量からポンプ・弁流量と出入口差圧を求める
        self.g = g
        self.flag = 0
        if self.valve == None: # バイパス弁がない場合
            if self.pump.inv == 0: # ポンプ停止時
                self.pump.g = 0.0
                self.dp = 0
            else:
                self.pump.g = self.g / self.num
                self.dp = - self.kr_pipe_pump * self.pump.g**2 + self.pump.f2p(self.pump.g)
        else: # バイパス弁もポンプもある場合            
            if self.valve.vlv == 0: # バイパス弁全閉時
                self.valve.g = 0.0
                self.pump.g = self.g / self.num
                self.dp = - self.kr_pipe_pump * self.pump.g**2 + self.pump.f2p(self.pump.g)
            elif self.pump.inv == 0: # ポンプ停止時、バイパス弁が開いている時
                self.pump.g = 0.0
                self.valve.g = self.g
                self.dp = - self.kr_pipe_valve * self.valve.g**2 + self.valve.f2p(self.valve.g)
            else:
                [co_0a, co_1a, co_2a] = self.pump.f2p_co() + np.array([0, 0, -self.kr_pipe_pump]) # 二次関数の係数の算出
                [co_0b, co_1b, co_2b] = self.valve.f2p_co() + np.array([0, 0, -self.kr_pipe_valve])
                # co_0a + co_1a*self.pump.g + co_2a*self.pump.g**2 = - co_2b*self.valve.g**2
                # self.num*self.pump.g - self.valve.g = self.g
                # 上記二式をポンプ流量の式に変形した二次方程式の係数は以下のようになる
                [co_0c, co_1c, co_2c] = [co_0a + co_2b*self.g**2, co_1a - co_2b*2*self.num*self.g, co_2a + co_2b*self.num**2]
                [self.pump.g, flag] = quadratic_formula(co_0c, co_1c, co_2c)
                self.valve.g = self.num*self.pump.g - self.g
                self.dp = - self.kr_pipe_pump * self.pump.g**2 + self.pump.f2p(self.pump.g)
                # print("koko?",self.pump.g,self.num,self.g)
        return self.dp
    
    def p2f(self, dp): # 圧力差から流量を求める
        self.dp = dp
        self.flag = 0
        if self.valve == None: # バイパス弁がない場合 
            if self.dp > 0:
                if self.pump.inv == 0: #　ポンプ停止時の対応
                    self.g = 0.0
                    self.pump.f2p(self.g)
                    self.flag = 4
                else:
                    [co_0, co_1, co_2] = self.pump.f2p_co() + np.array([-self.dp, 0, -self.kr_pipe_pump])
                    [self.pump.g, self.flag] = quadratic_formula(co_0, co_1, co_2)
                    self.g = self.pump.g*self.num

            else:
                self.g = 0.0
                self.pump.f2p(self.g)
                self.flag = 5
                
        else: # ポンプもバイパス弁もある場合
            self.dp = dp
            self.flag = 0
            if self.valve.vlv == 0 and self.pump.inv == 0:
                self.valve.g = 0.0
                self.pump.g = 0.0
                
            elif self.valve.vlv == 0:
                self.valve.g = 0
                [co_0, co_1, co_2] = self.pump.f2p_co() + np.array([-self.dp, 0, -self.kr_pipe_pump])
                [self.pump.g, self.flag] = quadratic_formula(co_0, co_1, co_2)
                self.g = self.pump.g*self.num
                
            elif self.pump.inv == 0:
                self.pump.g = 0.0
                [co_0, co_1, co_2] = self.valve.f2p_co() + np.array([self.dp, 0, -self.kr_pipe_valve])
                [self.valve.g, self.flag] = quadratic_formula(co_0, co_1, co_2)
                if co_2 < 0 and self.dp > 0:
                    self.valve.g = (-self.dp / co_2)**0.5
                elif co_2 < 0 and self.dp < 0:
                    self.valve.g = -(self.dp / co_2)**0.5 # 逆流する
                else:
                    self.valve.g = 0.0
                    self.flag = 5
                self.g = self.valve.g
                
            else:
                # ポンプの流量
                [co_0, co_1, co_2] = self.pump.f2p_co() + np.array([-self.dp, 0, -self.kr_pipe_pump])
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
                [co_0, co_1, co_2] = self.valve.f2p_co() + np.array([self.dp, 0, -self.kr_pipe_valve])
                
                if co_2 < 0 and self.dp > 0:
                    self.valve.g = (-self.dp / co_2)**0.5
                elif co_2 < 0 and self.dp < 0:
                    self.valve.g = -(self.dp / co_2)**0.5 # 逆流する
                else:
                    self.valve.g = 0.0
                    self.flag = 5
                
            self.g = self.pump.g*self.num - self.valve.g
            
        return self.g
    
    def y2x_func(self, co_0, co_1, co_2, y): 
        if co_1**2-4*co_2*(co_0-y)>0:
            x1 = (-co_1+(co_1**2-4*co_2*(co_0-y))**0.5)/(2*co_2)
            x2 = (-co_1-(co_1**2-4*co_2*(co_0-y))**0.5)/(2*co_2)
            x = max(x1,x2)            
            if x < 0:
                x = 0.0            
        else:
            x=0
        return x
    
    def f2p_co(self,y_h): # coefficient for f2p
        # y_h:近似式の精度を高めたい中心値（苦肉の策）
        # バイパス弁の有無で場合分け
        if self.valve == None:
            [co_p0, co_p1, co_p2] = self.pump.f2p_co() + np.array([0, 0, -self.kr_pipe_pump])
            [co_p0, co_p1, co_p2] = [co_p0, co_p1/self.num, co_p2/self.num**2]
            [co_0, co_1, co_2] = [co_p0, co_p1, co_p2] # 二次関数の係数の算出
        elif self.valve.vlv == 0:
            [co_p0, co_p1, co_p2] = self.pump.f2p_co() + np.array([0, 0, -self.kr_pipe_pump])
            [co_p0, co_p1, co_p2] = [co_p0, co_p1/self.num, co_p2/self.num**2]
            [co_0, co_1, co_2] = [co_p0, co_p1, co_p2] # 二次関数の係数の算出
            
        else:
            # 近似式による係数算出
            [co_p0, co_p1, co_p2] = self.pump.f2p_co() + np.array([0, 0, -self.kr_pipe_pump])
            [co_p0, co_p1, co_p2] = [co_p0, co_p1/self.num, co_p2/self.num**2]
            [co_v0, co_v1, co_v2] = self.valve.f2p_co() + np.array([0, 0, -self.kr_pipe_valve])
            # x1_min = self.y2x_func(co_p0, co_p1, co_p2+co_v2, 0)
            # y1_max = (-co_v2)*x1_min**2
            
            y1 = [y_h-5+i for i in range(11)]
            x1 = [self.y2x_func(co_p0, co_p1, co_p2, y1[i]) for i in range(11)]
            if co_v2 < 0:
                x2 = [(y1[i]/(-co_v2))**0.5 for i in range(11)]
            else:
                x2 = [0 for i in range(11)]

            n1 = sum(x>0 for x in x1)
            x1 = x1[:n1]
            x2 = x2[:n1]
            y1 = np.array(y1[:n1])
            x3 = np.array(x1)-np.array(x2)
            
            [co_2, co_1, co_0]=np.polyfit(x3, y1, 2)
            
        return [co_0, co_1, co_2]


# 水系
class Branch_w: # 水配管の基本的な枝（ポンプ（並列ポンプ（バイパス弁付き）ユニットも可）、弁、機器が直列に並んだ基本的な枝）
    # コンポジションというpython文法を使う
    # def __init__()の中の値はデフォルト値。指定しなければこの値で計算される。
    def __init__(self, pump=None, valve=None, kr_eq=0.0, kr_pipe=0.0, actual_head=0.0):
        # pump        :ポンプのオブジェクト。並列ポンプ（バイパス弁付き）のオブジェクトも挿入可能
        # valve       :二方弁のオブジェクト
        # kr_eq       :機器の圧損係数[kPa/(m3/min)^2]
        # kr_pipe  　 :配管の圧損係数[kPa/(m3/min)^2]
        # actual_head :実揚程[m]。冷却塔などで水を汲み上げる必要がある場合に用いる
        # dp          :枝の出入口差圧[kPa]加圧：+, 減圧：-
        # g           :枝の出入口での流量[m3/min]
        # flag        :計算の順当性確認のためのフラグ
        self.rho = 993.326    # 37℃水の密度[kg/m3]
        self.ga = 9.8         # 重力加速度[m/s2]
        self.pump = pump
        self.valve = valve
        self.kr_eq = kr_eq
        self.kr_pipe = kr_pipe
        self.actual_head = actual_head * self.rho * self.ga / 1000   # 実揚程を[m]から[kPa]に変換
        self.dp = 0.0
        self.g = 0.0
        self.flag = 0
    
    def f2p(self, g): # 流量から圧力差を求める
        self.g = g
        self.flag = 0
        if self.pump == None and self.valve == None: # ファンもダンパもない場合
            if self.g > 0:
                self.dp = - self.kr_eq*self.g**2 - self.kr_pipe*self.g**2 - self.actual_head
            else: # 逆流する場合
                self.dp = self.kr_eq*self.g**2 + self.kr_pipe*self.g**2
                self.flag = 1
        
        elif self.pump == None: # 二方弁がある場合
            if self.g > 0:
                self.dp = - self.kr_eq*self.g**2 - self.kr_pipe*self.g**2 + self.valve.f2p(self.g) - self.actual_head
            else: # 逆流する場合
                self.dp = self.kr_eq*self.g**2 + self.kr_pipe*self.g**2 - self.valve.f2p(self.g)
                self.flag = 2
        
        elif self.valve == None: # ポンプがある場合
            if self.pump.para == 0: # Pump_paraでない場合
                if self.pump.inv == 0.0: #　ポンプ停止時の対応
                    self.dp = 0.0
                    self.g = 0.0
                    self.pump.f2p(self.g)
                else:
                    if self.g > 0:
                        self.dp = - self.kr_eq*self.g**2 - self.kr_pipe*self.g**2 + self.pump.f2p(self.g) - self.actual_head
                    else: # 逆流する場合 # この条件が適切かは要確認!!!!!!!!!!!!!!!!!!!!
                        self.g = 0.0
                        self.dp = self.pump.f2p(self.g)
                        self.flag = 3
            else: # Pump_paraの場合
                if self.pump.pump.inv == 0.0: #　ポンプ停止時の対応
                    self.dp = 0.0
                    self.g = 0.0
                    self.pump.f2p(self.g)
                else:
                    if self.g > 0:
                        self.dp = - self.kr_eq*self.g**2 - self.kr_pipe*self.g**2 + self.pump.f2p(self.g) - self.actual_head
                    else: # 逆流する場合 # この条件が適切かは要確認!!!!!!!!!!!!!!!!!!!!
                        self.g = 0.0
                        self.dp = self.pump.f2p(self.g)
                        self.flag = 3
                        
                    
        
        else: # ポンプも弁もある場合
            if self.pump.para == 0: # Pump_paraでない場合
                if self.pump.inv == 0.0: #　ポンプ停止時の対応
                    self.dp = 0.0
                    self.g = 0.0
                    self.pump.f2p(self.g)
                else:
                    if self.g > 0:
                        self.dp = - self.kr_eq*self.g**2 - self.kr_pipe*self.g**2 + self.pump.f2p(self.g) + self.valve.f2p(self.g) - self.actual_head
                    else: # 逆流する場合 # この条件が適切かは要確認!!!!!!!!!!!!!!!!!!!!
                        self.g = 0.0
                        self.dp = self.pump.f2p(self.g)
                        self.flag = 4
            else: # Pump_paraの場合
                if self.pump.pump.inv == 0.0: #　ポンプ停止時の対応
                    self.dp = 0.0
                    self.g = 0.0
                    self.pump.f2p(self.g)
                else:
                    if self.g > 0:
                        self.dp = - self.kr_eq*self.g**2 - self.kr_pipe*self.g**2 + self.pump.f2p(self.g) + self.valve.f2p(self.g) - self.actual_head
                    else: # 逆流する場合 # この条件が適切かは要確認!!!!!!!!!!!!!!!!!!!!
                        self.g = 0.0
                        self.dp = self.pump.f2p(self.g)
                        self.flag = 4     
        
        return self.dp
        
    def p2f(self, dp): # 圧力差から流量を求める
        self.dp = dp
        self.flag = 0
        if self.pump == None and self.valve == None: # ポンプも二方弁もない場合
            if self.dp < 0:
                [co_0, co_1, co_2] = np.array([self.dp - self.actual_head, 0, self.kr_eq + self.kr_pipe]) # 二次関数の係数の算出
                [self.g, self.flag] = quadratic_formula(co_0, co_1, co_2)
            else: # 逆流する場合
                [co_0, co_1, co_2] = np.array([-self.dp, 0, self.kr_pipe + self.kr_eq]) # 二次関数の係数の算出
                [g, flag] = quadratic_formula(co_0, co_1, co_2)
                self.g = -g
                self.flag = 1
            
        elif self.pump == None: # 二方弁がある場合
            if self.dp < 0:
                [co_0, co_1, co_2] = self.valve.f2p_co() + np.array([-self.dp - self.actual_head, 0, -self.kr_eq-self.kr_pipe])
                [self.g, self.flag] = quadratic_formula(co_0, co_1, co_2)
                self.valve.f2p(self.g)
            else: # 逆流する場合
                [co_0, co_1, co_2] = self.valve.f2p_co() + np.array([self.dp, 0, -self.kr_eq-self.kr_pipe])
                [g, flag] = quadratic_formula(co_0, co_1, co_2)
                self.g = -g
                self.valve.f2p(self.g)
                self.flag = 3
        
        elif self.valve == None: # ポンプがある場合
            
            # print(self.pump.f2p_co(),co_0, co_1, co_2)
            
            if self.pump.para == 0: # Pump_paraでない場合
                [co_0, co_1, co_2] = self.pump.f2p_co() + np.array([-self.dp - self.actual_head, 0, -self.kr_eq-self.kr_pipe])
                if self.pump.inv == 0: #　ポンプ停止時の対応
                    self.g = 0.0
                    self.pump.f2p(self.g)
                    self.flag = 4
                else:
                    # print("CP1", [co_0, co_1, co_2])
                    [self.g, self.flag] = quadratic_formula(co_0, co_1, co_2)
                    self.pump.f2p(self.g)   
                 
            else: # Pump_paraの場合
                [co_0, co_1, co_2] = self.pump.f2p_co(y_h=self.dp) + np.array([-self.dp - self.actual_head, 0, -self.kr_eq-self.kr_pipe])
                if self.pump.pump.inv == 0: #　ポンプ停止時の対応
                    self.g = 0.0
                    self.pump.f2p(self.g)
                    self.flag = 4
                else:
                    # print("CP1s", [co_0, co_1, co_2])
                    [self.g, self.flag] = quadratic_formula(co_0, co_1, co_2)
                    self.pump.f2p(self.g)
                    
                    
        else: # ポンプも二方弁もある場合
            if self.pump.para == 0: # Pump_paraでない場合
                [co_0, co_1, co_2] = self.pump.f2p_co() + self.valve.f2p_co() + np.array([-self.dp - self.actual_head, 0, -self.kr_eq-self.kr_pipe])
                if self.pump.inv == 0: #　ファン停止時の対応
                    self.g = 0.0
                    self.pump.f2p(self.g)
                    self.valve.f2p(self.g)
                    self.flag = 4
                else:
                    [self.g, self.flag] = quadratic_formula(co_0, co_1, co_2)
                    self.pump.f2p(self.g)
                    self.valve.f2p(self.g)
            else: # Pump_paraの場合
                [co_0, co_1, co_2] = self.pump.f2p_co(y_h=self.dp) + self.valve.f2p_co() + np.array([-self.dp - self.actual_head, 0, -self.kr_eq-self.kr_pipe])
                if self.pump.pump.inv == 0: #　ファン停止時の対応
                    self.g = 0.0
                    self.pump.f2p(self.g)
                    self.valve.f2p(self.g)
                    self.flag = 4
                else:
                    [self.g, self.flag] = quadratic_formula(co_0, co_1, co_2)
                    self.pump.f2p(self.g)
                    self.valve.f2p(self.g)
            
        return self.g

# ポンプ、機器、バイパス弁を有する枝
class Branch001: # コンポジションというpython文法を使う
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


# 空気系
# ファン・ダンパ・機器が直列に1台以下の枝。デフォルトではファン・ダンパ・機器はなし。
class Branch100: # コンポジションというpython文法を使う
    # def __init__()の中の値はデフォルト値。指定しなければこの値で計算される。
    def __init__(self, fan=None, damper=None, kr_eq=0.0, kr_duct=0.5):
        # fan       :ファンのオブジェクト
        # damper    :ダンパのオブジェクト
        # kr_eq     :機器の圧損係数[Pa/(m3/min)^2]
        # kr_duct   :ダクトの圧損係数[Pa/(m3/min)^2]
        # dp        :枝の出入口差圧[Pa]加圧：+, 減圧：-
        # flag      :計算の順当性確認のためのフラグ
        self.fan = fan
        self.damper = damper
        self.kr_eq = kr_eq
        self.kr_duct = kr_duct
        self.dp = 0.0
        self.g = 0.0
        self.flag = 0
    
    def f2p(self, g): # 流量から圧力差を求める
        self.g = g
        # print("test3")
        if self.fan == None and self.damper == None: # ファンもダンパもない場合
            if self.g > 0:
                self.dp = - self.kr_duct*self.g**2 - self.kr_eq*self.g**2
            else: # 逆流する場合
                self.dp = self.kr_duct*self.g**2 + self.kr_eq*self.g**2
        
        elif self.fan == None: # ダンパがある場合
            if self.g > 0:
                self.dp = - self.kr_duct*self.g**2 - self.kr_eq*self.g**2 + self.damper.f2p(self.g)
            else: # 逆流する場合
                self.dp = self.kr_duct*self.g**2 + self.kr_eq*self.g**2 - self.damper.f2p(self.g)
        
        elif self.damper == None: # ファンがある場合
            if self.fan.inv == 0.0: #　ファン停止時の対応
                self.dp = 0.0
                self.g = 0.0
                self.fan.f2p(self.g)
            else:
                if self.g > 0:
                    print("test2")
                    self.dp = - self.kr_duct*self.g**2 - self.kr_eq*self.g**2 + self.fan.f2p(self.g)
                else: # 逆流する場合
                    self.g = 0.0
                    self.dp = self.fan.f2p(self.g)
        
        else: # ファンもダンパもある場合
            if self.fan.inv == 0.0: #　ファン停止時の対応
                self.dp = 0.0
                self.g = 0.0
                self.fan.f2p(self.g)
            else:
                if self.g > 0:
                    self.dp = - self.kr_duct*self.g**2 - self.kr_eq*self.g**2 + self.fan.f2p(self.g) + self.damper.f2p(self.g)
                else: # 逆流する場合
                    self.g = 0.0
                    self.dp = self.fan.f2p(self.g)
        
        return self.dp
        
    def p2f(self, dp): # 圧力差から流量を求める
        self.dp = dp
        self.flag = 0
        if self.fan == None and self.damper == None: # ファンもダンパもない場合
            if -self.dp > 0:
                [co_0, co_1, co_2] = np.array([-self.dp, 0, -self.kr_duct-self.kr_eq]) # 二次関数の係数の算出
                [self.g, self.flag] = quadratic_formula(co_0, co_1, co_2)
            else:
                [co_0, co_1, co_2] = np.array([-self.dp, 0, self.kr_duct+self.kr_eq]) # 二次関数の係数の算出
                [g, flag] = quadratic_formula(co_0, co_1, co_2)
                self.g = -g
                self.flag = 3
            
        elif self.fan == None: # ダンパがある場合
            if -self.dp > 0:
                [co_0, co_1, co_2] = self.damper.f2p_co() + np.array([-self.dp, 0, -self.kr_duct-self.kr_eq])
                [self.g, self.flag] = quadratic_formula(co_0, co_1, co_2)
            else:
                [co_0, co_1, co_2] = self.damper.f2p_co() + np.array([-self.dp, 0, self.kr_duct+self.kr_eq])
                [g, flag] = quadratic_formula(co_0, co_1, co_2)
                self.g = -g
                self.flag = 3
        
        elif self.damper == None: # ファンがある場合
            [co_0, co_1, co_2] = self.fan.f2p_co() + np.array([-self.dp, 0, -self.kr_duct-self.kr_eq])
            if self.fan.inv == 0: #　ファン停止時の対応
                self.g = 0.0
                self.fan.f2p(self.g)
                self.flag = 4
            else:
                [self.g, self.flag] = quadratic_formula(co_0, co_1, co_2)
                
        else: # ファンもダンパもある場合
            [co_0, co_1, co_2] = self.fan.f2p_co() + self.damper.f2p_co() + np.array([-self.dp, 0, -self.kr_duct-self.kr_eq])
            if self.fan.inv == 0: #　ファン停止時の対応
                self.g = 0.0
                self.fan.f2p(self.g)
                self.damper.f2p(self.g)
                self.flag = 4
            else:
                [self.g, self.flag] = quadratic_formula(co_0, co_1, co_2)
            
        if self.fan != None:
            self.fan.g = self.g
            
        return self.g


