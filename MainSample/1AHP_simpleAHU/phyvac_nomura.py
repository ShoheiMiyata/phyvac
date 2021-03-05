# 熱源システムのシステムシミュレーションプログラム
# main文

import numpy as np
import math
import pandas as pd

# 機器関係モデル ###############################################################
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

    def cal(self, g, tin, q_load):
        self.g = g
        self.tin = tin
        self.q_load = q_load
        self.flag = 0
        self.tout = tin + q_load / 4.184 / self.g
        if self.tout > 25:
            self.tout = 25
            self.flag = 1
        self.q = (self.tout - self.tin) * self.g * 4.184

        self.dp = -self.kr * self.g ** 2

        return self.tout

    def f2p(self, g):
        self.g = g
        self.dp = -self.kr * self.g ** 2
        return self.dp

    def f2p_co(self):
        return [0, 0, -self.kr]

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

    def f2p(self, g):  # flow to pressure
        self.g = g
        # cv = self.cv_max * self.r**(self.vlv - 1)
        # self.dp = - 1743 * (self.g * 1000 / 60)**2 / cv**2 イコールパーセント特性
        if (self.cv_max * self.r ** (self.vlv - 1)) ** 2 > 0:
            self.dp = (- 1743 * (1000 / 60) ** 2 / (self.cv_max * self.r ** (self.vlv - 1)) ** 2) * self.g ** 2
        else:
            self.dp = 0

        return self.dp

    def p2f(self, dp):
        self.dp = dp
        if self.dp < 0:
            self.g = (self.dp / ((- 1743 * (1000 / 60) ** 2 / (self.cv_max * self.r ** (self.vlv - 1)) ** 2))) ** 0.5
        else:
            self.g = - (self.dp / (
            (1743 * (1000 / 60) ** 2 / (self.cv_max * self.r ** (self.vlv - 1)) ** 2))) ** 0.5  # 逆流

        return self.g

    def f2p_co(self):  # coefficient for f2p
        return np.array([0, 0, (- 1743 * (1000 / 60) ** 2 / (self.cv_max * self.r ** (self.vlv - 1)) ** 2)])


# ポンプ特性と消費電力計算
class Pump:
    # 定格値の入力
    def __init__(self, pg=[233, 5.9578, -4.95], eg=[0.0099, 0.4174, -0.0508], r_ef=0.8):
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

    def f2p(self, g):  # flow to pressure for pump
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

# 空冷ヒートポンプ
class AirSourceHeatPump:
    # 定格値の入力
    def __init__(self, tin_ch_d=12, tout_ch_d=7, g_ch_d=0.116, kr_ch=13.9, signal_hp=1,
                 coef=[[40.0, -6.2468, 15.891, -14.257, 4.2438, 2.3663],
                       [35.0, -10.355, 26.218, -23.497, 7.516, 2.4734],
                       [30.0, -9.3779, 24.859, -23.505, 7.8729, 2.9472],
                       [25.0, -7.4934, 19.994, -18.946, 5.8718, 3.8933],
                       [20.0, -6.5604, 17.853, -17.511, 5.4774, 4.6122],
                       [15.0, -6.2842, 17.284, -17.138, 5.228, 5.4071]]):  # 冷房時
        # def __init__(self, tin_ch_d=40, tout_ch_d=45, g_ch_d=0.172, kr_ch=13.9, signal_hp=2,
        #              coef= [[15.0, 0.3229, 0.6969, -2.8192, 2.0081, 2.8607],
        #              　　　  [7.0, 11.637, -24.052, 16.027, -3.7671, 2.8691],
        #                     [5.0, 12.552, -22.918, 13.204, -2.5234, 2.601],
        #                     [0.0, -3.2873, 3.2973, -2.2795, 1.2208, 2.0051],
        #                     [-5.0, 9.563, -27.733, 21.397, -5.8191, 2.4375]]):  # 暖房時
        # tin        :入口水温[℃]
        # tout       :出口水温[℃]
        # g          :流量[m3/min]
        # ch         :冷水(chilled water)
        # d          :定格値
        # sv         :現時刻の制御する要素の設定値(温度や圧力)
        # pw         :消費電力[kW]
        # pl         :部分負荷率(0.0~1.0)  part-load ratio
        # kr         :圧力損失係数[kPa/(m3/min)**2]
        # da         :外気乾球
        # signal     :運転信号(1=cooling, 2=heating)
        # COP = a * pl^4 + b * pl^3 + c * pl^2 + d^1 + e
        # coef = [[t1, a_t1, b_t1, c_t1, d_t1, e_t1], ... , [tn, a_tn, b_tn, c_tn, d_tn, e_tn]]
        # (a1_t1~e1_t1は、外気温t1のときのCOP曲線の4次～0次の係数、t1 >t2>...> tn, n>=3)
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
                pl = self.pl
                if pl > 1:
                    pl = 1
                    self.tout_ch = self.tin_ch - self.max_del_t * self.g_ch_d / self.g_ch
                elif pl < 0.2:
                    pl = 0.2

                if self.t_da >= self.coef[0][0]:
                    self.COP = (self.coef[0][1] * pl ** 4 + self.coef[0][2] * pl ** 3 +
                                self.coef[0][3] * pl ** 2 - self.coef[0][4] * pl + self.coef[0][5])
                elif self.t_da < self.coef[self.n - 1][0]:
                    self.COP = (self.coef[self.n - 1][1] * pl ** 4 + self.coef[self.n - 1][2] * pl ** 3 +
                                self.coef[self.n - 1][3] * pl ** 2 + self.coef[self.n - 1][4] * pl ** 3 +
                                self.coef[self.n - 1][5])
                else:
                    for i in range(1, self.n):  # 線形補間の上限・下限となる曲線を探す
                        self.coef_a = self.coef[i - 1]
                        self.coef_b = self.coef[i]
                        if self.coef_b[0] <= self.t_da < self.coef_a[0]:
                            break
                    a = (self.coef_a[1] * pl ** 4 + self.coef_a[2] * pl ** 3 + self.coef_a[3] * pl ** 2 +
                             self.coef_a[4] * pl + self.coef_a[5])
                    b = (self.coef_b[1] * pl ** 4 + self.coef_b[2] * pl ** 3 + self.coef_b[3] * pl ** 2 +
                             self.coef_b[4] * pl + self.coef_b[5])
                    self.COP = (a - b) * (self.coef_a[0] - self.t_da) / (self.coef_a[0] - self.coef_b[0]) + b
                # 消費電力の計算
                pw = (self.tin_ch - self.tout_ch) * self.g_ch / 60 * pow(10, 3) * 4.186 / self.COP
                if pw > 0:
                    self.pw = pw
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
                pl = self.pl
                if pl > 1:
                    pl = 1
                    self.tout_ch = self.tin_ch + self.max_del_t * self.g_ch_d / self.g_ch
                elif pl < 0.2:
                    pl = 0.2

                if self.t_da >= self.coef[0][0]:
                    self.COP = (self.coef[0][1] * pl ** 4 + self.coef[0][2] * pl ** 3 +
                                self.coef[0][3] * pl ** 2 - self.coef[0][4] * pl + self.coef[0][5])
                elif self.t_da < self.coef[self.n - 1][0]:
                    self.COP = (self.coef[self.n - 1][1] * pl ** 4 + self.coef[self.n - 1][2] * pl ** 3 +
                                self.coef[self.n - 1][3] * pl ** 2 + self.coef[self.n - 1][4] * pl ** 3 +
                                self.coef[self.n - 1][5])
                else:
                    for i in range(1, self.n):  # 線形補間の上限・下限となる曲線を探す
                        self.coef_a = self.coef[i - 1]  # higher limit curve
                        self.coef_b = self.coef[i]  # lower limit curve
                        if self.coef_b[0] <= self.t_da < self.coef_a[0]:
                            break
                    a = (self.coef_a[1] * pl ** 4 + self.coef_a[2] * pl ** 3 + self.coef_a[3] * pl ** 2 +
                             self.coef_a[4] * pl + self.coef_a[5])
                    b = (self.coef_b[1] * pl ** 4 + self.coef_b[2] * pl ** 3 + self.coef_b[3] * pl ** 2 +
                             self.coef_b[4] * pl + self.coef_b[5])
                    self.COP = (a - b) * (self.coef_a[0] - self.t_da) / (self.coef_a[0] - self.coef_b[0]) + b
                # 消費電力の計算
                pw = (self.tout_ch - self.tin_ch) * self.g_ch / 60 * pow(10, 3) * 4.178 / self.COP
                if pw > 0:
                    self.pw = pw
                else:
                    self.pw = 0
            else:
                self.tout_ch = self.tin_ch
                self.COP = 0
                self.pw = 0
                self.pl = 0

        return self.tout_ch, self.COP, self.pw, self.pl
    

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
        self.t_step_cnt = -1  # 計算ステップのための内部パラメータ
        self.a = 0

    def control(self, sv, mv):
        if self.mode == 1:

            self.t_step_cnt += 1
            if self.t_step_cnt % self.t_step == 0:
                self.t_step_cnt = 0

                self.sig += sv - mv
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


# 流量計算関係モデル ###########################################################
# 機器、バルブを有する枝
class Branch01():  # コンポジションというpython文法を使う
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

    def f2p(self, g):  # 流量から圧力損失を求める
        # (枝の圧損) = (管圧損) + (機器圧損) + (バルブ圧損)
        self.g = g
        self.dp = - self.kr_pipe * self.g ** 2 - self.kr_eq * self.g ** 2 + self.valve.f2p(self.g)
        return self.dp

    def p2f(self, dp):  # 圧力差から流量を求める
        self.dp = dp
        self.flag = 0

        [co_0, co_1, co_2] = self.valve.f2p_co() + np.array([-self.dp, 0, -self.kr_pipe - self.kr_eq])  # 二次関数の係数の算出

        if co_1 ** 2 - 4 * co_2 * co_0 > 0:
            g1 = (-co_1 + (co_1 ** 2 - 4 * co_2 * co_0) ** 0.5) / (2 * co_2)
            g2 = (-co_1 - (co_1 ** 2 - 4 * co_2 * co_0) ** 0.5) / (2 * co_2)
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
class Branch10():  # コンポジションというpython文法を使う
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
        self.dp = self.pump.f2p(self.g) - self.kr_pipe * self.g ** 2 - self.kr_eq * self.g ** 2
        return self.dp

    def p2f(self, dp):  # 圧力差から流量を求める
        self.dp = dp
        self.flag = 0
        [co_0, co_1, co_2] = self.pump.f2p_co() + np.array([-self.dp, 0, -self.kr_pipe - self.kr_eq])  # 二次関数の係数の算出
        if co_1 ** 2 - 4 * co_2 * co_0 > 0:
            g1 = (-co_1 + (co_1 ** 2 - 4 * co_2 * co_0) ** 0.5) / (2 * co_2)
            g2 = (-co_1 - (co_1 ** 2 - 4 * co_2 * co_0) ** 0.5) / (2 * co_2)
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


# 湿り空気曲線モデル ###########################################################
# 露点温度の算出
def dew_point_temperature(tdb, rh):
    # t_da      :外気乾球温度[℃]
    # rh        :外気相対湿度(0~100)
    # tsa       :露天温度['C]
    # 飽和水蒸気圧Ps[mmHg]の計算
    c = 373.16 / (273.16 + tdb)
    b = c - 1
    a = -7.90298 * b + 5.02808 * math.log10(c) - 1.3816 * 10 ** (-7) * (10 ** (11.344 * b / c) - 1) + 8.1328 * 10 ** (
        -3) * (10 ** (-3.49149 * b) - 1)
    Ps = 760 * 10 ** a
    # 入力した絶対湿度
    x = 0.622 * (rh * Ps) / 100 / (760 - rh * Ps / 100)

    # この絶対湿度で相対湿度100%となる飽和水蒸気圧Ps
    Ps = 100 * 760 * x / (100 * (0.622 + x))
    Ps0 = 0
    Tdpmax = tdb
    Tdpmin = -20
    tsa = 0
    cnt = 0
    # 飽和水蒸気圧が上のPsの値となる温度Twb
    while (Ps - Ps0 < -0.01) or (Ps - Ps0 > 0.01):

        tsa = (Tdpmax + Tdpmin) / 2

        c = 373.16 / (273.16 + tsa)
        b = c - 1
        a = -7.90298 * b + 5.02808 * math.log10(c) - 1.3816 * 10 ** (-7) * (
                    10 ** (11.344 * b / c) - 1) + 8.1328 * 10 ** (-3) * (10 ** (-3.49149 * b) - 1)
        Ps0 = 760 * 10 ** a

        if Ps - Ps0 > 0:
            Tdpmin = tsa
        else:
            Tdpmax = tsa

        cnt += 1
        if cnt > 30:
            break

    return tsa


# 比エンタルピーの算出
def enthalpy(tdb, rh):
    # 乾球温度tdbと相対湿度rhから比エンタルピーhと絶対湿度xを求める
    # h     :enthalpy [J/kg]
    # tdb   :Temperature of dry air ['C]
    # rh    :relative humidity [%]
    # cpd   :乾き空気の定圧比熱 [J / kg(DA)'C]
    # gamma :飽和水蒸気の蒸発潜熱 [J/kg]
    # cpv   :水蒸気の定圧比熱 [J / kg(DA)'C]
    # x     :絶対湿度 [kg/kg(DA)]

    cpd = 1007
    gamma = 2499 * 10 ** 3
    cpv = 1845

    # 飽和水蒸気圧Ps[mmHg]の計算
    c = 373.16 / (273.16 + tdb)
    b = c - 1
    a = -7.90298 * b + 5.02808 * math.log10(c) - 1.3816 * 10 ** (-7) * (10 ** (11.344 * b / c) - 1) + 8.1328 * 10 ** (
        -3) * (10 ** (-3.49149 * b) - 1)
    Ps = 760 * 10 ** a

    x = 0.622 * (rh * Ps) / 100 / (760 - rh * Ps / 100)

    h = cpd * tdb + (gamma + cpv * tdb) * x

    return [h, x]


# 乾球温度から飽和水蒸気圧[hPa]
def tdb2ps(tdb):
    # ps:飽和水蒸気圧[hPa]
    # Wagner equation
    x = (1 - (tdb + 273.15) / 647.3)
    ps = 221200 * math.exp((-7.76451 * x + 1.45838 * x ** 1.5 + -2.7758 * x ** 3 - 1.23303 * x ** 6) / (1 - x))
    return ps


# 乾球温度と相対湿度から湿球温度['C]
def tdb_rh2twb(tdb, rh):
    # pv:水蒸気分圧[hPa]
    ps = tdb2ps(tdb)
    pv_1 = rh / 100 * ps
    pv_2 = -99999
    twb = 0
    twbmax = 50
    twbmin = -50
    cnt = 0
    while abs(pv_1 - pv_2) > 0.01:
        twb = (twbmax + twbmin) / 2
        # Sprung equation
        pv_2 = tdb2ps(twb) - 0.000662 * 1013.25 * (tdb - twb)

        if pv_1 - pv_2 > 0:
            twbmin = twb
        else:
            twbmax = twb

        cnt += 1
        if cnt > 20:
            break

    return twb

