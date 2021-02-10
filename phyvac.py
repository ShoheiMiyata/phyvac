# -*- coding: utf-8 -*-
"""
@author: shhmy
"""
# phyvacモジュール。hvav + python ->phyvac
# 空調システムの計算を極力物理原理・詳細な制御ロジックに基づいて行う。現在は熱源システムが中心（2021.01.21）
# ver0.1 20210128


import numpy as np
import math


# 機器関係モデル ###############################################################

# 空冷ヒートポンプ
class RR:
    # 定格値の入力
    def __init__(self, tin_ch_d=12, tout_ch_d=7, g_ch_d=0.215, kr_ch=13.9, signal_hp=1):  # cooling mode
    # def __init__(self, tin_ch_d=40, tout_ch_d=45, g_ch_d=0.172, kr_ch=13.9, signal_hp=2):  # heating mode
        # tin        :入口温度[℃]
        # tout       :出口温度[℃]
        # g          :流量[m3/min]
        # ch         :冷水(chilled water)
        # cd         :冷却水(condenser water)
        # d          :定格値
        # sv         :現時刻の制御する要素の設定値(温度や圧力)
        # pw         :消費電力[kW]
        # lf         :部分負荷率(0.0~1.0)
        # kr         :圧力損失係数[kPa/(m3/min)**2]
        # da         :外気乾球
        # signal     :運転信号(1=cooling, 2=heating)
        self.tin_ch_d = tin_ch_d
        self.tout_ch_d = tout_ch_d
        self.g_ch_d = g_ch_d
        self.kr_ch = kr_ch
        self.signal_hp = signal_hp
        self.max_del_t = abs(self.tin_ch_d - self.tout_ch_d)

    def cal(self, tin_ch, g_ch, t_da):
        # 以下、毎時刻変わる可能性のある値
        self.t_da = t_da
        self.g_ch = g_ch
        self.tin_ch = tin_ch
        self.tout_ch = 7
        self.pw = 0
        self.lf = 0
        self.COP = 0
        # 冷房時のCOP曲線係数[4次, 3次, 2次 1次, 切片]
        self.c15 = [-6.2842, 17.2840, -17.1380, 5.2280, 5.4071]
        self.c20 = [-6.5604, 17.8530, -17.5110, 5.4774, 4.6122]
        self.c25 = [-7.4934, 19.9940, -18.9460, 5.8718, 3.8933]
        self.c30 = [-9.3779, 24.8590, -23.5050, 7.8729, 2.9472]
        self.c35 = [-10.3550, 26.2180, -23.4970, 7.5160, 2.4734]
        self.c40 = [-6.2468, 15.8910, -14.2570, 4.2438, 2.3663]
        # 暖房時のCOP曲線係数
        self.h15 = [0.3229, 0.6969, -2.8192, 2.0081, 2.8607]
        self.h07 = [11.6370, -24.0520, 16.0270, -3.7671, 2.8691]
        self.h05 = [12.5520, -22.9180, 13.2040, -2.5234, 2.6010]
        self.h00 = [-3.2873, 3.2973, -2.2795, 1.2208, 2.0051]
        self.h_05 = [9.5630, -27.7330, 21.3970, -5.8191, 2.4375]

        if self.signal_hp == 1:
            if (self.g_ch > 0) and (self.tin_ch > self.tout_ch_d):
                self.tout_ch = self.tout_ch_d
                self.lf = (self.tin_ch - self.tout_ch) * self.g_ch / (self.max_del_t * self.g_ch_d) # 最大出入口温度差[℃]、最大流量[m3/min]
                if self.lf > 1:
                    self.lf = 1
                    self.tout_ch = self.tin_ch - self.max_del_t * self.g_ch_d / self.g_ch
                elif self.lf < 0.2:
                    self.lf = 0.2

                if self.t_da < 15:  # 15度以下は15度として計算
                    self.COP = self.c15[0] * pow(self.lf, 4) + self.c15[1] * pow(self.lf, 3) \
                               + self.c15[2] * pow(self.lf, 2) + self.c15[3] * self.lf + self.c15[4]
                elif self.t_da < 20:
                    a = self.c15[0] * pow(self.lf, 4) + self.c15[1] * pow(self.lf, 3) \
                               + self.c15[2] * pow(self.lf, 2) + self.c15[3] * self.lf + self.c15[4]
                    b = self.c20[0] * pow(self.lf, 4) + self.c20[1] * pow(self.lf, 3) \
                               + self.c20[2] * pow(self.lf, 2) + self.c20[3] * self.lf + self.c20[4]
                    self.COP = b + (a - b) * (20 - self.t_da) / 5
                elif self.t_da < 25:
                    a = self.c20[0] * pow(self.lf, 4) + self.c20[1] * pow(self.lf, 3) \
                        + self.c20[2] * pow(self.lf, 2) + self.c20[3] * self.lf + self.c20[4]
                    b = self.c25[0] * pow(self.lf, 4) + self.c25[1] * pow(self.lf, 3) \
                        + self.c25[2] * pow(self.lf, 2) + self.c25[3] * self.lf + self.c25[4]
                    self.COP = b + (a - b) * (25 - self.t_da) / 5
                elif self.t_da < 30:
                    a = self.c25[0] * pow(self.lf, 4) + self.c25[1] * pow(self.lf, 3) \
                        + self.c25[2] * pow(self.lf, 2) + self.c25[3] * self.lf + self.c25[4]
                    b = self.c30[0] * pow(self.lf, 4) + self.c30[1] * pow(self.lf, 3) \
                        + self.c30[2] * pow(self.lf, 2) + self.c30[3] * self.lf + self.c30[4]
                    self.COP = b + (a - b) * (25 - self.t_da) / 5
                elif self.t_da < 35:
                    a = self.c30[0] * pow(self.lf, 4) + self.c30[1] * pow(self.lf, 3) \
                        + self.c30[2] * pow(self.lf, 2) + self.c30[3] * self.lf + self.c30[4]
                    b = self.c35[0] * pow(self.lf, 4) + self.c35[1] * pow(self.lf, 3) \
                        + self.c35[2] * pow(self.lf, 2) + self.c35[3] * self.lf + self.c35[4]
                    self.COP = b + (a - b) * (35 - self.t_da) / 5
                elif self.t_da < 40:
                    a = self.c35[0] * pow(self.lf, 4) + self.c35[1] * pow(self.lf, 3) \
                        + self.c35[2] * pow(self.lf, 2) + self.c35[3] * self.lf + self.c35[4]
                    b = self.c40[0] * pow(self.lf, 4) + self.c40[1] * pow(self.lf, 3) \
                        + self.c40[2] * pow(self.lf, 2) + self.c40[3] * self.lf + self.c40[4]
                    self.COP = b + (a - b) * (40 - self.t_da) / 5
                else:  # 40度以上は40度として計算
                    self.COP = self.c40[0] * pow(self.lf, 4) + self.c40[1] * pow(self.lf, 3) \
                               + self.c40[2] * pow(self.lf, 2) + self.c40[3] * self.lf + self.c40[4]
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
                self.lf = 0

        if self.signal_hp == 2:
            if (self.g_ch > 0) and (self.tin_ch < self.tout_ch_d):
                self.tout_ch = self.tout_ch_d
                self.lf = (self.tout_ch - self.tin_ch) * self.g_ch / (self.max_del_t * self.g_ch_d)
                if self.lf > 1:
                    self.lf = 1
                    self.tout_ch = self.tin_ch + self.max_del_t * self.g_ch_d / self.g_ch
                elif self.lf < 0.2:
                    self.lf = 0.2

                if self.t_da < -5:  # -5度以下は-5度として計算
                    self.COP = self.h_05[0] * pow(self.lf, 4) + self.h_05[1] * pow(self.lf, 3) \
                               + self.h_05[2] * pow(self.lf, 2) + self.h_05[3] * self.lf + self.h_05[4]
                elif self.t_da < 0:
                    a = self.h_05[0] * pow(self.lf, 4) + self.h_05[1] * pow(self.lf, 3) \
                        + self.h_05[2] * pow(self.lf, 2) + self.h_05[3] * self.lf + self.h_05[4]
                    b = self.h00[0] * pow(self.lf, 4) + self.h00[1] * pow(self.lf, 3) \
                        + self.h00[2] * pow(self.lf, 2) + self.h00[3] * self.lf + self.h00[4]
                    self.COP = b + (a - b) * (20 - self.t_da) / 5
                elif self.t_da < 5:
                    a = self.h00[0] * pow(self.lf, 4) + self.h00[1] * pow(self.lf, 3) \
                        + self.h00[2] * pow(self.lf, 2) + self.h00[3] * self.lf + self.h00[4]
                    b = self.h05[0] * pow(self.lf, 4) + self.h05[1] * pow(self.lf, 3) \
                        + self.h05[2] * pow(self.lf, 2) + self.h05[3] * self.lf + self.h05[4]
                    self.COP = b + (a - b) * (25 - self.t_da) / 5
                elif self.t_da < 7:
                    a = self.h05[0] * pow(self.lf, 4) + self.h05[1] * pow(self.lf, 3) \
                        + self.h05[2] * pow(self.lf, 2) + self.h05[3] * self.lf + self.h05[4]
                    b = self.h07[0] * pow(self.lf, 4) + self.h07[1] * pow(self.lf, 3) \
                        + self.h07[2] * pow(self.lf, 2) + self.h07[3] * self.lf + self.h07[4]
                    self.COP = b + (a - b) * (25 - self.t_da) / 5
                elif self.t_da < 15:
                    a = self.h07[0] * pow(self.lf, 4) + self.h07[1] * pow(self.lf, 3) \
                        + self.h07[2] * pow(self.lf, 2) + self.h07[3] * self.lf + self.h07[4]
                    b = self.h15[0] * pow(self.lf, 4) + self.h15[1] * pow(self.lf, 3) \
                        + self.h15[2] * pow(self.lf, 2) + self.h15[3] * self.lf + self.h15[4]
                    self.COP = b + (a - b) * (35 - self.t_da) / 5
                else: # 15度以上は15度として計算
                    self.COP = self.h15[0] * pow(self.lf, 4) + self.h15[1] * pow(self.lf, 3) \
                        + self.h15[2] * pow(self.lf, 2) + self.h15[3] * self.lf + self.h15[4]
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
                self.lf = 0

        return self.g_ch, self.tin_ch, self.tout_ch, self.COP, self.pw, self.lf

    
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
        
        
# 修正係数を用いた冷凍機COP計算。流量の入力はm3/minだが内部の計算ではl/minに変換していることに注意
class CentrifugalChiller:
    # 定格値の入力
    def __init__(self, tout_ch_d=7, tin_ch_d=15, g_ch_d=3.145, tin_cd_d=32, tout_cd_d=37, g_cd_d=5.925,pw_d=299.717,kr_ch=1.0, kr_cd = 1.1):
        # tin   :入口温度[℃]
        # tout  :出口温度[℃]
        # g     :流量[m3/min]
        # q     :熱量[kW]
        # ch    :冷水（chilled water）
        # cd    :冷却水(condenser water)
        # d     :定格値
        # pw    :消費電力[kW]  
        # qf    :部分負荷率(0.0~1.0)
        # rg    :定格に対する流量比(0.0~1.0)
        # kr_ch :蒸発器圧力損失係数[kPa/(m3/min)**2]
        # kr_cd :凝縮器圧力損失係数[kPa/(m3/min)**2]
        # dp    :機器による圧力損失[kPa]
        self.tout_ch_d = tout_ch_d
        self.tin_ch_d = tin_ch_d
        self.g_ch_d = g_ch_d
        self.tin_cd_d = tin_cd_d
        self.tout_cd_d = tout_cd_d
        self.g_cd_d = g_cd_d
        # 定格冷凍容量[kW]
        self.q_ch_d = (tin_ch_d - tout_ch_d)*g_ch_d*1000*4.186/60
        # 定格主電動機入力[kW]
        self.pw_d = pw_d
        self.kr_ch = kr_ch
        self.kr_cd = kr_cd
        # 補機電力[kW]
        self.pw_sub = 0
        # 定格冷凍機COP
        self.COP_rp = self.q_ch_d / pw_d
        # 以下、毎時刻変わる可能性のある値
        self.tout_ch = 7
        self.tout_cd = 37
        self.pw = 0
        self.q_ch = 0
        self.qf = 0 # 負荷率(0.0~1.0)
        self.rg_ch = 0
        self.rg_cd = 0
        self.hb = 0 # ヒートバランス。冷水・冷却水・消費電力のエネルギーバランス
        self.cop = 0
        self.flag = 0 #問題があったら1,なかったら0
        self.dp_ch = 0
        self.dp_cd = 0
        self.tin_cd = 15
        self.tin_ch = 7
    
    
    # 冷却水出口温度を入力とした冷凍機COPの算出（収束計算用）tout_ch<tout_cdでないと計算エラーとなる。
    def cal_sub(self):
        # 温度抵抗換算損失[K]
        Td = 0.4
        # 理想COP ########これを二種類設定した！！
        COP_id_d = (self.tout_ch_d + 273.15)/(self.tout_cd_d - self.tout_ch_d + Td)
        COP_id = (self.tout_ch + 273.15)/(self.tout_cd - self.tout_ch + Td)
        # 飽和圧力（蒸発器側、定格時） [MPa]
        P_e_d = 1.73147*10**(-9)*self.tout_ch_d**4 + 9.04915*10**(-7)*self.tout_ch_d**3 + 1.47774*10**(-4)*self.tout_ch_d**2 + 1.06096*10**(-2)*self.tout_ch_d + 2.93321*10**(-1)
        # 飽和圧力（凝縮器側、定格時） [MPa]
        P_c_d = 1.73147*10**(-9)*self.tout_cd_d**4 + 9.04915*10**(-7)*self.tout_cd_d**3 + 1.47774*10**(-4)*self.tout_cd_d**2 + 1.06096*10**(-2)*self.tout_cd_d + 2.93321*10**(-1)
        # 飽和圧力（蒸発器側、運転時） [MPa]
        P_e = 1.73147*10**(-9)*self.tout_ch**4 + 9.04915*10**(-7)*self.tout_ch**3 + 1.47774*10**(-4)*self.tout_ch**2 + 1.06096*10**(-2)*self.tout_ch + 2.93321*10**(-1)
        # 飽和圧力（凝縮器側、運転時） [MPa]
        P_c = 1.73147*10**(-9)*self.tout_cd**4 + 9.04915*10**(-7)*self.tout_cd**3 + 1.47774*10**(-4)*self.tout_cd**2 + 1.06096*10**(-2)*self.tout_cd + 2.93321*10**(-1)
        # 設計基準無次元数
        K100 = 19.4
        # 圧縮機所要ヘッド（定格使用条件）[m]
        H_adsp = (-0.00027254*self.tout_ch_d**2-0.0090244*self.tout_ch_d+47.941)*(math.log10(P_c_d)-math.log10(P_e_d))*1000/9.8067
        # 圧縮機所要ヘッド（運転条件）[m]
        H_ad = (-0.00027254*self.tout_ch**2-0.0090244*self.tout_ch+47.941)*(math.log10(P_c)-math.log10(P_e))*1000/9.8067
        # 比体積 [m3/kg]
        v_d = 1 / (0.007626*self.tout_ch_d**2 + 0.50887*self.tout_ch_d + 14.38)
        v = 1 / (0.007626*self.tout_ch**2 + 0.50887*self.tout_ch + 14.38)
        # 相対設計風量係数
        # print(H_ad, K100, P_e, P_c, self.tout_cd)
        Q_d = 0.1*(H_ad/K100)**0.5
        # 定格一段流量変数
        TH_sp = 0.0893
        # 設計一段流量変数
        TH_dp = 0.0717
        # 一段流量変数による修正係数
        Cf2 = TH_sp/TH_dp
        # 吸込冷媒比体積による修正係数
        Cf3 = v / v_d
        # 運転条件下での相対負荷係数
        # print(self.tout_ch, self.tout_cd)
        Qr = self.qf / Q_d * Cf2 * Cf3
    
        # 修正係数
        if Qr < 0.08:
            Qr = 0.08
        elif Qr > 2.12:
            Qr = 2.12
    
        Qr1 = Qr**0.1
        Cf1 = 3143.9702*Qr1**4 - 12170.8638*Qr1**3 + 17755.8144*Qr1**2 - 11574.6744*Qr1 + 2847.2746
        
        # 推定COP
        COP_ct0 = COP_id / Cf1
        # 推定COPの補正
        # 定格使用条件での相対設計風量係数
        Q_ddp = 0.1 * (H_adsp/K100)**0.5
        # 定格使用条件での圧縮機相対負荷係数 ####K/100(ここではQf)を定格のため1とした!
        Q_rdp = 1 / Q_ddp * Cf2 * Cf3
        # 定格使用条件での修正係数
        Q_rdp1 = Q_rdp**0.1
        Cf_dp1 = 3143.9702*Q_rdp1**4 - 12170.8638*Q_rdp1**3 + 17755.8144*Q_rdp1**2 - 11574.6744*Q_rdp1 + 2847.2746
        COP_dp = COP_id_d / Cf_dp1
    
        # 現状運転下COP
        COP_ct = COP_ct0 * self.COP_rp / COP_dp
        self.cop = COP_ct
        # 電力消費量[kW]
        self.pw = self.q_ch / COP_ct + self.pw_sub
        # ヒートバランス
        Q_cd = (self.tout_cd - self.tin_cd)*self.g_cd*1000*4.186/60
        self.hb = Q_cd / (self.q_ch + self.pw)
        self.tout_cd = (self.q_ch + self.pw)/(4.186*self.g_cd*1000/60) + self.tin_cd
    
    # 修正係数を用いた冷凍機COPの算出
    def cal(self,tout_ch_sv, tin_ch, g_ch, tin_cd, g_cd):
        self.tout_ch_sv = tout_ch_sv
        self.tin_ch = tin_ch
        self.g_ch = g_ch
        self.tin_cd = tin_cd
        self.g_cd = g_cd
        # 冷水出口温度[℃]
        self.tout_ch = self.tout_ch_sv
        # 冷凍熱量[kW]
        self.q_ch = (self.tin_ch - self.tout_ch)*self.g_ch*1000*4.186/60
        # print(self.q_ch, self.g_cd)
        if self.q_ch > 0 and self.g_cd > 0:
            # 部分負荷率
            self.qf = self.q_ch / self.q_ch_d
            if self.qf > 1.0:
                self.qf = 1.0
                self.tout_ch += (self.q_ch - self.q_ch_d)/(self.g_ch*1000*4.186/60)
                self.q_ch = self.q_ch_d

            # 冷水量比
            self.rg_ch = self.g_ch/self.g_ch_d
            # 冷却水量比
            self.rg_cd = self.g_cd/self.g_cd_d
            
            # ヒートバランスのとれる冷却水出口温度の算出
            self.hb = 0
            # print(self.tout_cd, self.tout_cd_d, self.tin_cd_d, self.qf,self.rg_cd,self.tin_cd)
            self.tout_cd = (self.tout_cd_d-self.tin_cd_d)*self.qf/self.rg_cd+self.tin_cd # 冷却水出口温度の初期値
            # print(self.tout_ch, self.tout_cd, self.tin_cd)
            if self.tout_ch < self.tin_cd: # 安全を取ってこの条件でないと停止するものとする。
                cnt = 0
                self.flag=0
                while self.hb < 0.999 or self.hb > 1.001: # 収束計算 
                    self.cal_sub() #class内の関数を呼び出すにはself.をつける
                    cnt += 1
                    if cnt == 100:
                        self.flag=1
                        break
            else:
                self.flag=2
                self.pw = 0
                self.cop = 0
                self.tout_cd = 10 # 計算を回すための仮想的な再熱器
                self.tout_ch = self.tin_ch
        elif self.q_ch == 0:
            self.pw = 0
            self.cop = 0
            # self.tout_cd = self.tin_cd
            self.flag = 0
        else:
            self.pw = 0
            self.cop = 0
            # self.tout_cd = self.tin_cd
            self.flag = 1
        
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
        self.flag = np.zeros(t_reset)
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
                t_reset = self.flag.size
                for ii in range(t_reset - 1, 0, -1):
                    self.flag[ii] = self.flag[ii - 1]
                if sv - mv > 0:
                    self.flag[0] = 1
                elif sv - mv < 0:
                    self.flag[0] = -1
                else:
                    self.flag[0] = 0
            
                if all(i == 1 for i in self.flag) == True or all(i == -1 for i in self.flag) == True:
                    self.sig = 0
                    self.flag = np.zeros(t_reset)
            
            
        elif self.mode == 0:
            self.a = 0
            
        return self.a

# 増減段閾値と効果待ち時間を有する台数制御   
class Unit_Num:
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
        self.flag = np.zeros(t_wait)
        self.g = 0      
            
    def control(self, g):
        self.g = g
        num_max = len(self.thre_up)+1
        
        for i in range(self.t_wait - 1, 0, -1):
            self.flag[i] = self.flag[i-1]
          
        if self.num == num_max:
            if self.g < self.thre_down[self.num-2]:
                self.flag[0] = self.num-1
        elif self.num == 1:
            if self.g > self.thre_up[self.num-1]:
                self.flag[0] = self.num+1
                
        elif self.g > self.thre_up[self.num-1]:
            self.flag[0] = self.num+1
        elif self.g < self.thre_down[self.num-2]:
            self.flag[0] = self.num-1
        else:
            self.flag[0] = self.num
            
        if self.flag[0] < 1:
            self.flag[0] = 1
        elif self.flag[0] > num_max:
            self.flag[0] = num_max
        
            
        if all(i > self.num for i in self.flag):
            self.num += 1
        elif all(i < self.num for i in self.flag):
            self.num -= 1
        
        return self.num
    
# 冷凍機台数制御
class Unit_Num_CC:
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
        self.flag = np.zeros(t_wait)
        self.g = 0      
            
    def control(self, g, q):
        self.g = g
        self.q = q
        num_max = len(self.thre_up_g)+1
        flag_g = 0
        flag_q = 0
        
        for i in range(self.t_wait - 1, 0, -1):
            self.flag[i] = self.flag[i-1]
        
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
            self.flag[0] = self.num+1
        elif flag_g == -1 and flag_q == -1:
            self.flag[0] = self.num-1
        else:
            self.flag[0] = self.num
        
        if all(i > self.num for i in self.flag):
            self.num += 1
        elif all(i < self.num for i in self.flag):
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
class Branch01(): # コンポジションというpython文法を使う
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
class Branch10(): # コンポジションというpython文法を使う
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
class Branch11(): # コンポジションというpython文法を使う
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
class Branch12(): # コンポジションというpython文法を使う
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




