# -*- coding: utf-8 -*-
"""
@author: shhmy
"""
# phyvacモジュール。hvav + python ->phyvac
# 空調システムの計算を極力物理原理・詳細な制御ロジックに基づいて行う。現在は熱源システムが中心（2021.01.21）
# ver0.1 20210128


import numpy as np
import math
import pandas as pd
from scipy.interpolate import RegularGridInterpolator


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
        self.dp = 0
        self.vlv = 0
        self.g = 0
        
    def f2p(self, g): # flow to pressure
        self.g = g
        # cv = self.cv_max * self.r**(self.vlv - 1)
        # self.dp = - 1743 * (self.g * 1000 / 60)**2 / cv**2 イコールパーセント特性
        if (self.cv_max * self.r**(self.vlv - 1))**2 > 0:
            self.dp = (- 1743 * (1000 / 60)**2 / (self.cv_max * self.r**(self.vlv - 1))**2) * self.g**2
        else:
            self.dp = 0
            
        return self.dp
    
    def p2f(self,dp):
        self.dp = dp
        if self.dp < 0:
            self.g = (self.dp/((- 1743 * (1000 / 60)**2 / (self.cv_max * self.r**(self.vlv - 1))**2)))**0.5
        else:
            self.g = - (self.dp/((1743 * (1000 / 60)**2 / (self.cv_max * self.r**(self.vlv - 1))**2)))**0.5 # 逆流
        
        return self.g
    
    def f2p_co(self): # coefficient for f2p
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
        self.inv = 0
        self.dp = 0
        self.g = 0
        self.ef = 0
        self.pw = 0
        self.flag = 0
        self.num = 1
    
    def f2p(self, g): # flow to pressure for pump
        self.g = g
        # 流量がある場合のみ揚程を計算する
        if self.g > 0 and self.inv > 0:
            self.dp = (self.pg[0] + self.pg[1] *  (self.g / self.inv) + self.pg[2] *  (self.g / self.inv)**2) * self.inv**2
        else:
            self.dp = 0
            
        if self.dp < 0:
            self.dp = 0
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
                self.dp = 0
                self.flag = 1
            # print(Nm)
        
            #  軸動力を求める
            if self.ef > 0:
                self.pw = 1.0 * self.g * self.dp / (60 * self.ef)
                self.flag = 0
            else:
                self.pw = 0
                self.flag = 2
            # print(self.flag)
        
        else:
            self.pw = 0.0
            self.flag = 0
        
        
# 負荷率-COP曲線に基づく冷凍機COP計算。表は左から右、上から下に負荷率や冷却水入口温度が上昇しなければならない。
class Chiller:
    # 定格値の入力
    def __init__(self, spec_table=pd.read_csv("chiller_spec_table.csv",encoding="SHIFT-JIS",header=None)):
        # tin   :入口温度[℃]
        # tout  :出口温度[℃]
        # g     :流量[m3/min]
        # q     :熱量[kW]
        # ch    :冷水（chilled water）
        # cd    :冷却水(condenser water)
        # d     :定格値
        # pw    :消費電力[kW]  
        # lf    :部分負荷率(load factor, 0.0~1.0)
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
        
        lf_cop = spec_table.drop(spec_table.index[[0, 1, 2]])
        lf_cop.iat[0,0] = '-'
        lf_cop = lf_cop.dropna(how='all', axis=1)
        self.data = lf_cop.values

        
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
             
            lf = self.data[0][1:].astype(np.float32)
            temp = self.data.transpose()[0][1:].astype(np.float32)
            dataset = self.data[1:].transpose()[1:].transpose().astype(np.float32)
            cop = RegularGridInterpolator((temp, lf), dataset)
            
            # 部分負荷率
            self.lf = self.q_ch / self.q_ch_d
            lf_cop = self.lf
            if self.lf > lf[-1]:
                self.lf = lf[-1]
                lf_cop = self.lf
                self.tout_ch += (self.q_ch - self.q_ch_d)/(self.g_ch*1000*4.186/60)
                self.q_ch = self.q_ch_d
                self.flag = 1

            elif self.lf < lf[0]:
                lf_cop = lf[-1]
                self.flag = 2
            
            tin_cd_cop = self.tin_cd-(self.tout_ch-self.tout_ch_d)
            
            if tin_cd_cop < temp[0]:
                tin_cd_cop = temp[0]
                self.flag = 3
            elif tin_cd_cop > temp[-1]:
                tin_cd_cop = temp[-1]
                self.flag = 4

            self.cop = float(cop([[tin_cd_cop, lf_cop]]))
            self.pw = self.q_ch / self.cop + self.pw_sub
            self.tout_cd = (self.q_ch + self.pw)/(4.186*self.g_cd*1000/60) + self.tin_cd
            
            
        elif self.q_ch == 0:
            self.pw = 0
            self.cop = 0
            # self.tout_cd = self.tin_cd
            self.flag = 0
        else:
            self.pw = 0
            self.cop = 0
            # self.tout_cd = self.tin_cd
            self.flag = 5
        
        self.dp_ch = -self.kr_ch*g_ch**2
        self.dp_cd = -self.kr_cd*g_cd**2
        

# 露点温度の算出
def dew_point_temperature(Tda, rh):
    # t_da      :外気乾球温度[℃]
    # rh        :外気相対湿度(0~100)
    # Tdp       :露天温度['C]
    # 飽和水蒸気圧Ps[mmHg]の計算
    c = 373.16 / (273.16 + Tda)
    b = c - 1
    a = -7.90298 * b + 5.02808 * math.log10(c) - 1.3816 * 10**(-7) * (10**(11.344 * b / c) - 1) + 8.1328 * 10**(-3) * (10**(-3.49149 * b) - 1)
    Ps = 760 * 10**a
    # 入力した絶対湿度
    x = 0.622 * (rh * Ps) / 100 / (760 - rh * Ps / 100)

    # この絶対湿度で相対湿度100%となる飽和水蒸気圧Ps
    Ps = 100 * 760 * x / (100 * (0.622 + x))
    Ps0 = 0
    Tdpmax = Tda
    Tdpmin = -20
    Tdp = 0
    cnt = 0
    # 飽和水蒸気圧が上のPsの値となる温度Twb
    while (Ps - Ps0 < -0.01)or(Ps - Ps0 > 0.01):
        
        Tdp = (Tdpmax + Tdpmin) / 2
        
        c = 373.16 / (273.16 + Tdp)
        b = c - 1
        a = -7.90298 * b + 5.02808 * math.log10(c) - 1.3816 * 10**(-7) * (10**(11.344 * b / c) - 1) + 8.1328 * 10**(-3) * (10**(-3.49149 * b) - 1)
        Ps0 = 760 * 10**a
        
        if Ps - Ps0 > 0:
            Tdpmin = Tdp
        else:
            Tdpmax = Tdp
        
        cnt += 1  
        if cnt > 30:
            break
        
    return Tdp


# 比エンタルピーの算出
def enthalpy(Tda, rh):
    # 乾球温度Tdaと相対湿度rhから比エンタルピーhと絶対湿度xを求める
    # h     :enthalpy [J/kg]
    # Tda   :Temperature of dry air ['C]
    # rh    :relative humidity [%]
    # cpd   :乾き空気の定圧比熱 [J / kg(DA)'C]
    # gamma :飽和水蒸気の蒸発潜熱 [J/kg]
    # cpv   :水蒸気の定圧比熱 [J / kg(DA)'C]
    # x     :絶対湿度 [kg/kg(DA)]
    
    cpd = 1007
    gamma = 2499 * 10**3
    cpv = 1845
    
    # 飽和水蒸気圧Ps[mmHg]の計算
    c = 373.16 / (273.16 + Tda)
    b = c - 1
    a = -7.90298 * b + 5.02808 * math.log10(c) - 1.3816 * 10**(-7) * (10**(11.344 * b / c) - 1) + 8.1328 * 10**(-3) * (10**(-3.49149 * b) - 1)
    Ps = 760 * 10**a
    
    x = 0.622 * (rh * Ps) / 100 / (760 - rh * Ps / 100)
    
    h = cpd * Tda + (gamma + cpv * Tda) * x
    
    return [h, x]


# 乾球温度から飽和水蒸気圧[hPa]
def tda2ps(tda):
    # ps:飽和水蒸気圧[hPa]
    # Wagner equation
    x = (1 - (tda+273.15)/647.3)
    ps = 221200*math.exp((-7.76451*x + 1.45838*x**1.5+-2.7758*x**3-1.23303*x**6)/(1-x))
    return ps

# 乾球温度と相対湿度から湿球温度['C]
def tda_rh2twb(tda, rh):
    # pv:水蒸気分圧[hPa]
    ps = tda2ps(tda)
    pv_1 = rh/100*ps
    pv_2 = -99999
    twb = 0
    twbmax = 50
    twbmin = -50
    cnt = 0
    while abs(pv_1-pv_2) > 0.01:
        twb = (twbmax + twbmin) / 2
        # Sprung equation
        pv_2 = tda2ps(twb)-0.000662*1013.25*(tda-twb)

        if pv_1-pv_2 > 0:
            twbmin = twb
        else:
            twbmax = twb
            
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
#         [h,x] = enthalpy(Tda,rh)
#         [hs,xs] = enthalpy(Twb,100)
#         Twb0 = (hs - h) / ((xs - x) * cpw)
        
#         if Twb - Twb0 > 0:
#             Twbmin = Twb
#         else:
#             Twbmax = Twb
          
#         cnt += 1
#         if cnt > 30:
#             break
    
#     return Twb


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
            [hin,xin] = enthalpy(Tda,rh)
            Twbin = tda_rh2twb(Tda,rh)
            
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
                [hout, xout] = enthalpy(Twbout0,100)
                
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
        self.tout = tin + q_load / 4.184 / self.g
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
        
# 空冷ヒートポンプ
class AirSourceHeatPump:
    # 定格値の入力
    def __init__(self, tin_ch_d=12, tout_ch_d=7, g_ch_d=0.116, kr_ch=13.9, signal_hp=1,
                 coef=[[40.0, -6.2468, 15.891, -14.257, 4.2438, 2.3663],
                       [35.0, -10.355, 26.218, -23.497, 7.516, 2.4734],
                       [30.0, -9.3779, 24.859, -23.505, 7.8729, 2.9472],
                       [25.0, -7.4934, 19.994, -18.946, 5.8718, 3.8933],
                       [20.0, -6.5604, 17.853, -17.511, 5.4774, 4.6122],
                       [15.0, -6.2842, 17.284, -17.138, 5.228, 5.4071]]):
        # def __init__(self, tin_ch_d=40, tout_ch_d=45, g_ch_d=0.172, kr_ch=13.9, signal_hp=2,
        #              coef= [[15.0, 0.3229, 0.6969, -2.8192, 2.0081, 2.8607], [7.0, 11.637, -24.052, 16.027, -3.7671, 2.8691],
        #                     [5.0, 12.552, -22.918, 13.204, -2.5234, 2.601], [0.0, -3.2873, 3.2973, -2.2795, 1.2208, 2.0051],
        #                     [-5.0, 9.563, -27.733, 21.397, -5.8191, 2.4375]]):
        # tin        :入口水温[℃]
        # tout       :出口水温[℃]
        # g          :流量[m3/min]
        # ch         :冷水(chilled water)
        # d          :定格値
        # sv         :現時刻の制御する要素の設定値(温度や圧力)
        # pw         :消費電力[kW]
        # pl         :部分負荷率(part-load ratio 0.0~1.0)
        # kr         :圧力損失係数[kPa/(m3/min)**2]
        # da         :外気乾球
        # signal     :運転信号(1=cooling, 2=heating)
        # COP = a * pl^4 + b * pl^3 + c * pl^2 + d^1 + e
        # coef = [[t1, a_t1, b_t1, c_t1, d_t1, e_t1], ... , [tn, a_tn, b_tn, c_tn, d_tn, e_tn]]
        # (a1_t1~e1_t1は、外気温t1のときのCOP曲線の係数、t1 >t2>...> tn, n>=3)
        self.tin_ch_d = tin_ch_d
        self.tout_ch_d = tout_ch_d
        self.g_ch_d = g_ch_d
        self.kr_ch = kr_ch
        self.signal_hp = signal_hp
        self.coef = coef
        self.n = len(self.coef)
        self.max_del_t = abs(self.tin_ch_d - self.tout_ch_d)  # 最大出入口温度差[℃]
        # 以下、毎時刻変わる可能性のある値
        self.tout_ch = 7
        self.COP = 0
        self.pw = 0
        self.pl = 0

    def cal(self, tin_ch, g_ch, t_da):
        self.tin_ch = tin_ch
        self.g_ch = g_ch
        self.t_da = t_da

        if self.signal_hp == 1:
            if (self.g_ch > 0) and (self.tin_ch > self.tout_ch_d):
                self.tout_ch = self.tout_ch_d
                self.pl = (self.tin_ch - self.tout_ch) * self.g_ch / (self.max_del_t * self.g_ch_d)
                if self.pl > 1:
                    self.pl = 1
                    self.tout_ch = self.tin_ch - self.max_del_t * self.g_ch_d / self.g_ch
                elif self.pl < 0.2:
                    self.pl = 0.2

                if self.t_da >= self.coef[0][0]:
                    self.COP = (self.coef[0][1] * self.pl ** 4 + self.coef[0][2] * self.pl ** 3 +
                                self.coef[0][3] * self.pl ** 2 - self.coef[0][4] * self.pl + self.coef[0][5])
                elif self.t_da < self.coef[self.n - 1][0]:
                    self.COP = (self.coef[self.n - 1][1] * self.pl ** 4 + self.coef[self.n - 1][2] * self.pl ** 3 +
                                self.coef[self.n - 1][3] * self.pl ** 2 + self.coef[self.n - 1][4] * self.pl ** 3 +
                                self.coef[self.n - 1][5])
                else:
                    for i in range(1, self.n):  # 線形補間の上限・下限となる曲線を探す
                        self.coef_a = self.coef[i - 1]
                        self.coef_b = self.coef[i]
                        if self.coef_b[0] <= self.t_da < self.coef_a[0]:
                            break
                    a = (self.coef_a[1] * self.pl ** 4 + self.coef_a[2] * self.pl ** 3 + self.coef_a[3] * self.pl ** 2 +
                             self.coef_a[4] * self.pl + self.coef_a[5])
                    b = (self.coef_b[1] * self.pl ** 4 + self.coef_b[2] * self.pl ** 3 + self.coef_b[3] * self.pl ** 2 +
                             self.coef_b[4] * self.pl + self.coef_b[5])
                    self.COP = (a - b) * (self.coef_a[0] - self.t_da) / (self.coef_a[0] - self.coef_b[0]) + b
                # 消費電力の計算
                self.pw = (self.tin_ch - self.tout_ch) * self.g_ch / 60 * pow(10, 3) * 4.186 / self.COP
                if self.pw > 0:
                    pass
                else:
                    self.pw = 0
            else:
                self.tout_ch = self.tin_ch
                self.COP = 0
                self.pw = 0
                self.pl = 0

        if self.signal_hp == 2:
            if (self.g_ch > 0) and (self.tin_ch < self.tout_ch_d):
                self.tout_ch = self.tout_ch_d
                self.pl = (self.tout_ch - self.tin_ch) * self.g_ch / (self.max_del_t * self.g_ch_d)
                if self.pl > 1:
                    self.pl = 1
                    self.tout_ch = self.tin_ch + self.max_del_t * self.g_ch_d / self.g_ch
                elif self.pl < 0.2:
                    self.pl = 0.2

                if self.t_da >= self.coef[0][0]:
                    self.COP = (self.coef[0][1] * self.pl ** 4 + self.coef[0][2] * self.pl ** 3 +
                                self.coef[0][3] * self.pl ** 2 - self.coef[0][4] * self.pl + self.coef[0][5])
                elif self.t_da < self.coef[self.n - 1][0]:
                    self.COP = (self.coef[self.n - 1][1] * self.pl ** 4 + self.coef[self.n - 1][2] * self.pl ** 3 +
                                self.coef[self.n - 1][3] * self.pl ** 2 + self.coef[self.n - 1][4] * self.pl ** 3 +
                                self.coef[self.n - 1][5])
                else:
                    for i in range(1, self.n):  # 線形補間の上限・下限となる曲線を探す
                        self.coef_a = self.coef[i - 1]  # higher limit curve
                        self.coef_b = self.coef[i]  # lower limit curve
                        if self.coef_b[0] <= self.t_da < self.coef_a[0]:
                            break
                    a = (self.coef_a[1] * self.pl ** 4 + self.coef_a[2] * self.pl ** 3 + self.coef_a[3] * self.pl ** 2 +
                             self.coef_a[4] * self.pl + self.coef_a[5])
                    b = (self.coef_b[1] * self.pl ** 4 + self.coef_b[2] * self.pl ** 3 + self.coef_b[3] * self.pl ** 2 +
                             self.coef_b[4] * self.pl + self.coef_b[5])
                    self.COP = (a - b) * (self.coef_a[0] - self.t_da) / (self.coef_a[0] - self.coef_b[0]) + b
                # 消費電力の計算
                self.pw = (self.tout_ch - self.tin_ch) * self.g_ch / 60 * pow(10, 3) * 4.178 / self.COP
                if self.pw > 0:
                    pass
                else:
                    self.pw = 0
            else:
                self.tout_ch = self.tin_ch
                self.COP = 0
                self.pw = 0
                self.pl = 0

        return self.tout_ch, self.COP, self.pw, self.pl

    
# ダンパ特性と圧力損失計算
class Damper():
    def cal(self, g, damp,
            coef=[[1.0,-0.00001944,0.018,0.18,-0.007], [0.8,0.0000864,0.036,0.132,0.0684],
                 [0.6,0.001296,0.072,0.384,0.1001], [0.4,0.00108,0.36,-0.582,0.0662], [0.2,-0.0216,4.32,-5.34,0.2527]]):
        # damp  :ダンパ開度[0.0~1.0]
        # dp    :圧力損失[Pa]
        # g     :流量[m^3/min]
        # dp = a * g^3 + b * g^2 + c * g + d
        # coef = [[damp1, a_damp1, b_damp1, c_damp1, d_damp1], ... , [dampn, a_dampn, b_dampn, c_dampn, d_dampn]]  (x1 >...> xn, n>=3)
        self.g = g
        self.damp = damp
        self.coef = coef
        n = len(self.coef)
        if self.damp >= self.coef[0][0]:
            self.dp = (self.coef[0][1] * self.g ** 3 + self.coef[0][2] * self.g ** 2 + self.coef[0][3] * self.g + self.coef[0][4])
        elif self.damp < self.coef[n-1][0]:
            self.dp = (self.coef[n-1][1] * self.g ** 3 + self.coef[n-1][2] * self.g ** 2 + self.coef[n-1][3] * self.g + self.coef[n-1][4])
        else:
            for i in range(1, n):    # 線形補間の上限・下限となる曲線を探す
                self.hl = self.coef[i-1]  # higher limit curve
                self.ll = self.coef[i]    # lower limit curve
                if self.ll[0] <= self.damp < self.hl[0]:
                    break
            dp_h = (self.hl[1] * self.g ** 3 + self.hl[2] * self.g ** 2 + self.hl[3] * self.g + self.hl[4])
            dp_l = (self.ll[1] * self.g ** 3 + self.ll[2] * self.g ** 2 + self.ll[3] * self.g + self.ll[4])
            self.dp = (dp_h - dp_l) / (self.hl[0]-self.ll[0]) * (self.damp - self.ll[0]) + dp_l
        return self.dp
    

# 制御関係モデル ###############################################################

# pid制御（プログラムの中身はd成分を無視したpi制御）
class PID:
    # def __init__()の中の値はデフォルト値。指定しなければこの値で計算される。
    def __init__(self, mode=1, a_max=1, a_min=0, kp=0.8, ti=10, t_reset=30, kg=1, sig=0, t_step=1):
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
            self.valve_pid.sig = 0　#切り替わる際に積分リセット（安定性向上のため）
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
    def __init__(self, thre_up=[0.5,1.0], thre_down=[0.4,0.9], t_wait=15):
        # thre_up_g     :増段閾値(1->2, 2->3といった時の値。型は配列またはリストとする) thre: threshold, g: 流量, q: 熱量
        # thre_down_q   :減段閾値(2->1, 3->2といった時の値。型は配列またはリストとする)
        # t_wait        :効果待ち時間(ex: 15分)
        # num           :運転台数 num: number
        # g             :流量[m3/min]
        # q             :熱量[kW]
        self.thre_up = thre_up
        self.thre_down = thre_down
        self.t_wait = t_wait
        self.num = 1
        self.flag_switch = np.zeros(t_wait)
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
        self.dp = 0
        self.g = 0
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
                self.g = 0
                self.flag = 1
            else:
                self.g = max(g1, g2)
        else:
            self.g = 0
            self.flag = 1  
        return self.g     

# 機器、バルブを有する枝
class Branch01: # コンポジションというpython文法を使う
    # def __init__()の中の値はデフォルト値。指定しなければこの値で計算される。
    def __init__(self, valve, kr_eq=0.5, kr_pipe=0.5):
        # g         :枝の出入口流量[m3/min]
        # dp        :枝の出入口圧力差[kPa]加圧：+, 減圧：-
        # kr_pipe      :管の圧損係数[kPa/(m3/min)^2]
        # kr_eq      :機器の圧損係数[kPa/(m3/min)^2]
        # valve     :バルブのオブジェクト
        # vlv       :バルブ開度(1:全開,0:全閉)
        self.valve = valve
        self.kr_eq = kr_eq
        self.kr_pipe = kr_pipe
        self.dp = 0
        self.g = 0
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
                self.g = 0
                self.flag = 1
            else:
                self.g = max(g1, g2)
        else:
            self.g = 0
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
        self.dp = 0
        self.g = 0
        self.flag = 0
    
    def f2p(self, g):
        self.g = g
        # 枝の出入口差圧=ポンプ加圧-配管圧損-機器圧損
        self.dp = self.pump.f2p(self.g) - self.kr_pipe*self.g**2 - self.kr_eq*self.g**2
        return self.dp
        
    def p2f(self, dp): # 圧力差から流量を求める
        self.dp = dp
        self.flag = 0
        [co_0, co_1, co_2] = self.pump.f2p_co() + np.array([-self.dp, 0, -self.kr_pipe-self.kr_eq]) # 二次関数の係数の算出
        if co_1**2 - 4*co_2*co_0 > 0:
            g1 = (-co_1 + (co_1**2 - 4*co_2*co_0)**0.5)/(2 * co_2)
            g2 = (-co_1 - (co_1**2 - 4*co_2*co_0)**0.5)/(2 * co_2)
            if max(g1, g2) < 0:
                self.g = 0
                self.flag = 1
            else:
                self.g = max(g1, g2)
        else:
            self.g = 0
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
        self.g = 0
        self.dp = 0
        self.flag = 0
        
    def f2p(self, g): # 流量から圧力損失を求める
        self.g = g
        self.flag = 0
        
        if self.valve.vlv == 0:
            self.valve.g = 0
            self.pump.g = self.g / self.pump.num
            self.dp = - self.kr_pipe_pump * self.pump.g**2 + self.pump.f2p(self.pump.g)
        if self.pump.inv == 0 and self.valve.vlv > 0:
            self.pump.g = 0
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
                    self.pump.g = 0
                    self.flag = 1
                else:
                    self.pump.g = max(g1, g2)
            else:
                self.pump.g = 0
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
        self.g = 0
        self.dp = 0
        self.flag = 0
        
    def p2f(self, dp): # 圧力から流量を求める dp=0でも流れる？？
        self.dp = dp
        self.flag = 0
        if self.valve.vlv == 0 and self.pump.inv == 0:
            self.valve.g = 0
            self.pump.g = 0
            
        elif self.valve.vlv == 0:
            self.valve.g = 0
            [co_0, co_1, co_2] = self.pump.f2p_co() + np.array([-self.dp, 0, -self.kr_pipe-self.kr_eq])
            if co_1**2 - 4*co_2*co_0 > 0:
                g1 = (-co_1 + (co_1**2 - 4*co_2*co_0)**0.5)/(2 * co_2)
                g2 = (-co_1 - (co_1**2 - 4*co_2*co_0)**0.5)/(2 * co_2)
                if max(g1, g2) < 0:
                    self.pump.g = 0
                    self.flag = 1
                else:
                    self.pump.g = max(g1, g2)
            else:
                self.pump.g = 0
                self.flag = 1
                
        elif self.pump.inv == 0:
            self.pump.g = 0
            [co_0, co_1, co_2] = self.valve.f2p_co() + np.array([self.dp, 0, -self.kr_pipe_bypass])
            
            if co_2 < 0 and self.dp < 0:
                self.valve.g = (self.dp / co_2)**0.5
            elif co_2 < 0 and self.dp > 0:
                self.valve.g = -(self.dp / -co_2)**0.5 # 逆流する
            else:
                self.valve.g = 0
                self.flag = 2
            
        else:
            # ポンプの流量
            [co_0, co_1, co_2] = self.pump.f2p_co() + np.array([-self.dp, 0, -self.kr_pipe-self.kr_eq])
            if co_1**2 - 4*co_2*co_0 > 0:
                g1 = (-co_1 + (co_1**2 - 4*co_2*co_0)**0.5)/(2 * co_2)
                g2 = (-co_1 - (co_1**2 - 4*co_2*co_0)**0.5)/(2 * co_2)
                if max(g1, g2) < 0:
                    self.pump.g = 0
                    self.flag = 3
                else:
                    self.pump.g = max(g1, g2)
            else:
                self.pump.g = 0
                self.flag = 4
                
            # バイパス弁流量
            [co_0, co_1, co_2] = self.valve.f2p_co() + np.array([self.dp, 0, -self.kr_pipe_bypass])
            
            if co_2 < 0 and self.dp > 0:
                self.valve.g = (-self.dp / co_2)**0.5
            elif co_2 < 0 and self.dp < 0:
                self.valve.g = -(self.dp / co_2)**0.5 # 逆流する
            else:
                self.valve.g = 0
                self.flag = 5
            
        self.g = self.pump.g - self.valve.g
        
        return self.g




