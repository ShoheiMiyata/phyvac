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