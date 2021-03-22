import math
from scipy import optimize

#########################
# 空気調和・衛生工学会編：空気調和・衛生工学便覧14版，1基礎編，第3章, pp.39-56，2010.
# 式の読み方↓
# tdb_w2h   [input]tdb(dry-bulb temperature), w(absolute humidity) -> [output] h(enthalpy)
#########################

# psychrometric_functions.py←pyhvac.py
# ・tdb_rh2tdp(tdb, rh)    ← dew_point_temperature(Tda, rh)
# ・tdb_rh2h_x(tdb,rh)     ← enthalpy(Tda, rh)
# ・tdb2psat(tdb)          ← tda2ps(tda)
# ・tdb_rh2twb(tdb, rh)  　← tda_rh2twb(tda, rh)


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
