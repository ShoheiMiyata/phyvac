import math
from scipy import optimize

# HEXの計算準備として、psychrometric functionsを定義する

#########################
# sub-functions
#########################
# psychrometric functions

def tdb_w2h(tdb, w):
    ca = 1.005  # 乾き空気の定圧比熱 [kJ/kg・K]
    cv = 1.805  # 水蒸気の定圧比熱 [kJ/kg・K]
    r0 = 2.501 * 10 ** 3  # 0℃の水の蒸発潜熱 [kJ/kg]
    h = ca * tdb + (cv * tdb + r0) * w
    return h


def tdb2hsat(tdb):
    ps = tsat2psat(tdb)
    ws = pv2w(ps)
    hsat = tdb_w2h(tdb, ws)
    return hsat


def w2pv(w, p_atm=101.325):  # pressure of vapor
    pv = p_atm * w / (0.628198 + w)
    return pv


def pv2w(pv, p_atm=101.325):
    w = 0.62198 * pv / (p_atm - pv)
    return w


def tsat2psat(tsat):
    # find saturate pressure from temperature
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

    ts = tsat + 273.15
    if tsat < 0.01:
        psat = math.exp(
            c1 / ts + c2 + c3 * ts + c4 * ts ** 2 + c5 * ts ** 3 + c6 * ts ** 4 + c7 * math.log(ts)) * p_convert
        return psat
    else:
        alpha = ts + n9 / (ts - n10)
        a2 = alpha ** 2
        a = a2 + n1 * alpha + n2
        b = n3 * a2 + n4 * alpha + n5
        c = n6 * a2 + n7 * alpha + n8
        psat = pow(2 * c / (-b + pow(b ** 2 - 4 * a * c, 0.5)), 4) / p_convert
        return psat


def h_rh2w(h, rh):
    tdb = h_rh2tdb(h, rh)
    w = tdb_rh2w(tdb, rh)
    return w


def tdb2den(tdb):  # 気体の密度 [kg/m^3]
    den = 1.293 * 273.3 / (273.2 + tdb)
    return den


def h_rh2tdb(h, rh):
    fh = h
    frh = rh

    def h_rh2tdb_fun(tdb):
        return fh - tdb_rh2h(tdb, frh)

    return optimize.newton(h_rh2tdb_fun, x0=1e-5, tol=1e-4, maxiter=20)


def tdb_rh2h(tdb, rh):
    w = tdb_rh2w(tdb, rh)
    h = tdb_w2h(tdb, w)
    return h


def tdb_rh2w(tdb, rh):
    psat = tsat2psat(tdb)
    pw = 0.01 * rh * psat
    w = pv2w(pw)
    return w


def psat2tsat(psat):
    # saturation conditon
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
        tsat = d1 + y * (d2 + y * (d3 + y * d4))
        return tsat
    else:
        ps = psat * p_convert
        beta = pow(ps, 0.25)
        b2 = beta ** 2
        e = b2 + n3 * beta + n6
        f = n1 * b2 + n4 * beta + n7
        g = n2 * b2 + n5 * beta + n8
        d = 2 * g / (-f - pow(f ** 2 - 4 * e * g, 0.5))
        tsat = (n10 + d - pow((n10 + d) ** 2 - 4 * (n9 + n10 * d), 0.5)) / 2 - 273.15
        return tsat


def w_h2tdb(w, h):
    tdb = (h - 2501 * w) / (1.005 + 1.805 * w)
    return tdb


def w_rh2tdb(w, rh):
    ps = w2pv(w)
    tdb = psat2tsat(ps / rh * 100)
    return tdb


def w2cpair(w):
    cpair = 1.005 + 1.805 * w
    return cpair


def w_tdb2rh(w, tdb):
    pw = w2pv(w)
    ps = tsat2psat(tdb)
    if ps <= 0:
        return 0
    else:
        return pw / ps * 100


def tdb_twb2w(tdb, twb):
    ps = tsat2psat(twb)
    ws = pv2w(ps)
    a = ws * (2501 + (1.805 - 4.186) * twb) + 1.005 * (twb - tdb)
    b = 2501 + 1.805 * tdb - 4.186 * twb
    return a / b


def getparameter_hex(tdb):
    delta = 0.001
    hws1 = tdb2hsat(tdb)
    hws2 = tdb2hsat(tdb + delta)
    fa = (hws2 - hws1) / delta
    fb = hws1 - fa * tdb
    return fa, fb


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


def hex_ntu(feff, fratio_heat_cap, fflowtype):
    # flowtype : {'counterflow', 'parallelflow'}
    hex_eff = feff
    hex_ratio = fratio_heat_cap
    hex_flowtype = fflowtype

    def hex_efunc(fntu):
        return hex_eff - hex_effectiveness(fntu, hex_ratio, hex_flowtype)

    return optimize.newton(hex_efunc, x0=0, tol=1e-6, maxiter=20)  # rtol=1e-6 fprime=1e-4,


class Coil:
    def __init__(self, g_air_d=2.99, v_air_d=20.99, tdbin_air_d=27.2, twbin_air_d=20.1,
                 g_water_d=1.9833333, v_water_d=2.99, tin_water_d=7, q_d=40.4, rhborder=95):
        # q_load    :負荷熱量[GJ/min]
        # d         :定格
        # q         :熱交換能力[kw]
        # g         :流量[kg/s]
        # v         :速度[m/s]
        # t         :温度[℃]
        # in, out   :入口, 出口
        # db, wb    :乾球, 湿球
        # ntu       :移動単位数(熱容量流量に対する熱交換器の能力)[-]
        # eff       :熱通過有効度[-]
        # rhborder  :境界湿度[%]
        self.g_air_d = g_air_d
        self.v_air_d = v_air_d
        self.tdbin_air_d = tdbin_air_d
        self.twbin_air_d = twbin_air_d
        self.win_air_d = tdb_twb2w(self.tdbin_air_d, self.twbin_air_d)
        self.g_water_d = g_water_d
        self.v_water_d = v_water_d
        self.tin_water_d = tin_water_d
        self.q_d = q_d
        self.rhborder = rhborder
        self.g_air = 0
        self.tin_air = 0
        self.win_air = 0
        self.g_water = 0
        self.tin_water = 0
        self.tborder_water = self.tborder_air = 0
        self.zd = self.wd = self.v1 = self.v2 = self.zw = self.ww = self.v3 = self.v4 = self.v5 = self.v6 = 0
        self.tout_air = self.tout_water = self.wout_air = self.rhout_air = self.ratio_drywet = 0
        self.cpma = self.cap_air = self.cap_water = 0
        self.v_air = self.v_water = 0
        self.coef_dry = self.coef_wet = 0

        # heat transfer coefficient dry-[kW/(m^2*K)]   wet-[kW/(m^2*(kJ/kg))]
        coef_dry_d = 1 / (4.72 + 4.91 * pow(self.v_water_d, -0.8) + 26.7 * pow(self.v_air_d, -0.64))
        coef_wet_d = 1 / (10.044 + 10.44 * pow(self.v_water_d, -0.8) + 39.6 * pow(self.v_air_d, -0.64))

        # surface area
        cpma_d = w2cpair(self.win_air_d)
        cap_air_d = self.g_air_d * cpma_d
        cap_water_d = self.g_water_d * 4.186

        if self.tdbin_air_d < self.tin_water_d:
            # heating coil
            cap_min_d = min(cap_air_d, cap_water_d)
            cap_max_d = max(cap_air_d, cap_water_d)
            eff_d = self.q_d / cap_min_d / (self.tin_water_d - self.tdbin_air_d)
            ntu_d = hex_ntu(eff_d, cap_min_d / cap_max_d, 'counterflow')
            self.area_surface = ntu_d * cap_min_d / coef_dry_d

        else:
            # cooling coil
            self.tout_water_d = self.tin_water_d + self.q_d / cap_water_d
            self.hin_air_d = tdb_w2h(self.tdbin_air_d, self.win_air_d)
            self.hout_air_d = self.hin_air_d - self.q_d / self.g_air_d

            # wet condition
            self.wout_air_d = h_rh2w(self.hout_air_d, self.rhborder)

            if self.win_air_d < self.wout_air_d:
                # dry condition
                self.t_air_outlet_d = self.tdbin_air_d - self.q_d / cap_air_d
                d1_d = self.tdbin_air_d - self.tout_water_d
                d2_d = self.t_air_outlet_d - self.tin_water_d
                lmtd_d = (d1_d - d2_d) / math.log(d1_d / d2_d)
                self.area_surface = self.q_d / lmtd_d / coef_dry_d
            else:
                # dry+wet condition
                # air condition in border
                tborder_air_d = w_rh2tdb(self.win_air_d, self.rhborder)
                hborder_air_d = tdb_w2h(tborder_air_d, self.win_air_d)

                # water condition in border
                hborder_wet_d = (hborder_air_d - self.hout_air_d) * self.g_air_d
                tborder_water_d = self.tin_water_d + hborder_wet_d / cap_water_d

                # air saturation enthalpy that temperature equal to water
                hin_water_d = tdb2hsat(self.tin_water_d)
                hborder_water_d = tdb2hsat(tborder_water_d)

                # dry surface
                dt1_d = self.tdbin_air_d - self.tout_water_d
                dt2_d = tborder_air_d - tborder_water_d
                lmtd_d = (dt1_d - dt2_d) / math.log(dt1_d / dt2_d)
                area_dry_sur_d = (self.q_d - hborder_wet_d) / lmtd_d / coef_dry_d

                # wet surface
                dh1_d = hborder_air_d - hborder_water_d
                dh2_d = self.hout_air_d - hin_water_d
                lmhd_d = (dh1_d - dh2_d) / math.log(dh1_d / dh2_d)
                area_wet_sur_d = hborder_wet_d / lmhd_d / coef_wet_d

                self.area_surface = area_dry_sur_d + area_wet_sur_d

    def cal(self, g_air=5, tin_air=25, win_air=0.0118, g_water=0.3, tin_water=7):
        # when air or water flow rate is 0
        self.g_air = g_air
        self.tin_air = tin_air
        self.win_air = win_air
        self.g_water = g_water
        self.tin_water = tin_water

        if self.g_air <= 0 or self.g_water <= 0 or self.tin_air == self.tin_water:
            self.tout_air = self.tin_air
            self.tout_water = self.tin_water
            self.wout_air = self.win_air
            self.rhout_air = w_tdb2rh(self.wout_air, self.tout_air)
            self.ratio_drywet = 1
            q = 0
            return self.tout_air, self.wout_air, self.rhout_air, self.tout_water, self.ratio_drywet, q

        # capacity of water and wet air [kW/s]
        self.cpma = w2cpair(self.win_air)
        self.cap_air = self.g_air * self.cpma
        self.cap_water = self.g_water * 4.186

        # heat transfer coefficient dry-[kW/(m^2*K)]   wet-[kW/(m^2*(kJ/kg))]
        # proportion with water/air speed
        self.v_water = (self.g_water / self.g_water_d) * self.v_water_d
        self.v_air = (self.g_air / self.g_air_d) * self.v_air_d
        self.coef_dry = 1 / (4.72 + 4.91 * pow(self.v_water, -0.8) + 26.7 * pow(self.v_air, -0.64))
        self.coef_wet = 1 / (10.044 + 10.44 * pow(self.v_water, -0.8) + 39.6 * pow(self.v_air, -0.64))

        if self.tin_air < self.tin_water:  # heating
            ratio_drywet = 1
            cap_min = min(self.cap_air, self.cap_water)
            cap_max = max(self.cap_air, self.cap_water)
            ntu = self.coef_dry * self.area_surface / cap_min

            # efficient of heat gain
            eff = hex_effectiveness(ntu, cap_min / cap_max, 'counterflow')
            # outlet condition and heat change
            q = eff * cap_min * (self.tin_water - self.tin_air)
            tout_air = self.tin_air + q / self.cap_air
            tout_water = self.tin_water - q / self.cap_water
            wout_air = self.win_air
            rhout_air = w_tdb2rh(wout_air, tout_air)

        else:  # cooling
            # consider as saturate temperature
            tborder = w_rh2tdb(self.win_air, self.rhborder)
            h_air_inlet = tdb_w2h(self.tin_air, self.win_air)

            # saturation enthalpy based on Tdb
            # p_a parameter of temperature
            # p_b slice
            [p_a, p_b] = getparameter_hex(self.tin_water)
            xd = 1 / self.cap_air
            yd = -1 / self.cap_water
            xw = 1 / self.g_air
            yw = -p_a / self.cap_water

            def efunc(self, fdrate):
                self.fdrate = fdrate
                self.zd = math.exp(self.coef_dry * self.area_surface * self.fdrate * (xd + yd))
                self.wd = self.zd * xd + yd
                self.v1 = xd * (self.zd - 1) / self.wd
                self.v2 = self.zd * (xd + yd) / self.wd

                self.zw = math.exp(self.coef_wet * self.area_surface * (1 - self.fdrate) * (xw + yw))
                self.ww = self.zw * xw + yw
                self.v3 = (xw + yw) / self.ww
                self.v4 = xw * (self.zw - 1) / self.ww
                self.v5 = self.zw * (xw + yw) / self.ww
                self.v6 = yw * (1 - self.zw) / self.ww / p_a

                self.tborder_water = (self.v5 * self.tin_water + self.v6 * (h_air_inlet -
                                       self.v1 * self.cpma * self.tin_air - p_b)) / (1 - self.v1 * self.v6 * self.cpma)
                self.tborder_air = self.tin_air - self.v1 * (self.tin_air - self.tborder_water)
                if fdrate == 1 and self.tborder_air > tborder:
                    return 1
                return tborder - self.tborder_air

            # interaction to calculate dry-area
            drate = 1

            if 0 < efunc(drate):
                try:
                    drate = optimize.brentq(efunc, 0, 1, xtol=0.0001, maxiter=100)
                except ValueError:
                    drate = 0
                    efunc(drate)

            # outlet condition
            tout_water = self.tin_air - self.v2 * (self.tin_air - self.tborder_water)
            hborder_air = self.cpma * (self.tborder_air - self.tin_air) + h_air_inlet
            h_water_inlet = p_a * self.tin_water + p_b
            h_air_outlet = self.v3 * hborder_air + self.v4 * h_water_inlet
            q = self.cap_air * (self.tin_air - self.tborder_air) + self.g_air * (hborder_air - h_air_outlet)
            ratio_drywet = drate

            if drate < 1:
                wout_air = h_rh2w(h_air_outlet, self.rhborder)
            else:
                wout_air = self.win_air

            tout_air = w_h2tdb(wout_air, h_air_outlet)
            rhout_air = w_tdb2rh(wout_air, tout_air)

        return tout_air, wout_air, rhout_air, tout_water, ratio_drywet, q
