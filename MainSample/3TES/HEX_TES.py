import math

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
                    t_water_outlet_low = (
                                                     t_water_outlet_high - t_water_inlet_high) * flowrate_high / flowrate_low + t_water_inlet_low
                else:
                    t_water_outlet_low = t_water_inlet_high
                    t_water_outlet_high = (
                                                      t_water_outlet_low - t_water_inlet_low) * flowrate_low / flowrate_high + t_water_inlet_high
            if flag == 1:
                t_temp = t_water_outlet_high
                t_water_outlet_high = t_water_outlet_low
                t_water_outlet_low = t_temp
                flowrate_temp = flowrate_high
                flowrate_high = flowrate_low
                flowrate_low = flowrate_temp
                
        return flowrate_high, flowrate_low, t_water_inlet_high, t_water_inlet_low, t_water_outlet_high, t_water_outlet_low

