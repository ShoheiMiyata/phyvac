import numpy as np
import math
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 蓄熱槽モデル
# initial parameter

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


