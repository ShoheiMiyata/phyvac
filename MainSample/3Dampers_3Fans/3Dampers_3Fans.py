#####################################################
# 12/14 2018 18:16 soloved the bug of can't converge
# 12/14 2018 17:33 The most unfavorable loop must be in the calculation loop
# 11/25 2018 11:24 two floors in parallel while cycle
# g [m^3/min]
# 単位一律にPa, kW, lossはマイナス
# check the file name before run
#####################################################
import pandas as pd
from tqdm import tqdm

def flow_balance(inv_sa1, inv_ra1, inv_ea1, damp_ab, damp_ef, damp_eb):
    def dp_loss_damper(damp, g):
        coef_f2p = [[1.0, 0.0000203437802163088], [0.8, 0.0000495885440290287],
                    [0.6, 0.000143390887269431], [0.4, 0.000508875127863876], [0.2, 0.00351368187709778]]
        n = len(coef_f2p)
        g = g
        damp = damp
        if damp >= coef_f2p[0][0]:
            dp = coef_f2p[0][1] * g ** 2  # [kPa]
        elif damp < coef_f2p[n - 1][0]:
            dp = coef_f2p[n - 1][1] * g ** 2  # [kPa]
        else:
            for i in range(1, n):  # 線形補間の上限・下限となる曲線を探す
                coef_a = coef_f2p[i - 1]  # higher limit curve
                coef_b = coef_f2p[i]  # lower limit curve
                if coef_b[0] <= damp < coef_a[0]:
                    break
            a = coef_a[1] * g ** 2
            b = coef_b[1] * g ** 2
            dp = (a - b) / (coef_a[0] - coef_b[0]) * (damp - coef_b[0]) + b  # [kPa]
        return dp * (-1000)  # [Pa]

    def dp_fan(inv_fan, g, pg):
        # pg = [pq曲線の0次, 1次, 2次, 3次, 4次]の係数
        if inv_fan == 0:
            dp = 0
        else:
            dp = (pg[4] * (g / inv_fan) ** 4 + pg[3] * (g / inv_fan) ** 3 + pg[2] * (g / inv_fan) ** 2
                  + pg[1] * (g / inv_fan) + pg[0]) * inv_fan ** 2
        return dp

    def power_fan(g, dp, inv, b00, b01, b02, b03):  # dp[kPa]
        # ファンINV、流量、性能曲線かファン消費電力を計算する
        # pw        :ファン消費電力[kW]
        # inv       :ファンインバータ(0.0~1.0)
        # g         :流量[m3/min]
        # G         :定格流量[m3/min]
        # ef        :効率(0.0~1.0)
        # K         :効率換算係数（K=ef/N,Nは定格時の効率）
        # b         :効率曲線に関する定数
        # 効率は0~1の値とする!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # 流量と全揚程がある場合のみ消費電力を計算する
        if (g > 0) and (dp > 0):

            # INV=1.0時の流量を求める
            G = g / inv
            # 効率換算係数Kを求める
            K = 1
            # 効率を求める
            ef = K * (b00 + b01 * G + b02 * G ** 2 + b03 * pow(G, 3))  # [%]
            # 軸動力を求める
            if ef > 0:
                pw = g * dp / (60 * (ef / 100))
                flag = 0
            else:
                pw = 0.0
                flag = 1
        else:
            pw = 0.0
            ef = 0.0
            flag = 2

        return pw, flag


    p_atm = 101300  # [Pa]

    # 実験棟の圧力損失 Output2
    s_ab = -1.60483E-06 * 3600
    s_bc = -(1.76835E-08 + 1.41516E-06 + 8.42558E-07 + 2.23579E-05) * 3600 + 0.1
    s_gh = -0.01
    s_de = -(2.28926E-05 + 6.13053E-07 + 1.21993E-06 + 8.68733E-07) * 3600
    s_eb = -8.85798E-07 * 3600
    s_ef = -3.5456E-05 * 3600 - 3.39
    kr_AHU = -1.0   # 単位要確認
    # (s_ab, s_bc + kr_AHU, s_de, s_eb, s_ef, s_gh)=
    # (-0.005777388, -0.9886798854, -0.0921395376, -0.0031888728, -3.5176416, -0.01)

    # 一旦圧力損失を0.01で統一 Output3
    s_ab = -0.01
    s_bc = -0.01
    s_gh = -0.01
    s_de = -0.01
    s_eb = -0.01
    s_ef = -0.01
    kr_AHU = -1.0   # 単位要確認

    dp_SA1 = 498
    dp_RA1 = 0
    dp_EA1 = 0
    dp_loss_ab = 0
    dp_loss_bc = 0
    dp_loss_de = 0
    dp_loss_eb = 0
    dp_loss_ef = 0
    dp_loss_gh = 0
    g_ab_max = 50
    g_ab_min = 0

    # pg4次関数近似
    pg_SA1 = [494, -1.8337, 0.0372, -0.0005, 0]           # ①従来の単室計算SAファン性能曲線
    # pg_SA1 = [494, 0, 0, 0, 0]                          # ③単純化、494Paで固定(ASRAEに準拠)
    pg_RA1 = [318, -1.5863, 0.2251, -0.023, 0.0002]       # ⑥②で、切片を11.33㎥/minのときに298Paになるよう調整
    pg_EA1 = [176.62, -1.5863, 0.2251, -0.023, 0.0002]    # ②従来の単室計算EAファン性能曲線


    cnt0 = 0
    while abs(dp_loss_ab + dp_SA1 + dp_loss_bc + dp_loss_de + dp_RA1 + dp_loss_ef) > 0.01:
        g_ab = (g_ab_max + g_ab_min) / 2
        dp_loss_ab = s_ab * g_ab ** 2 + dp_loss_damper(damp_ab, g_ab)
        dp_SA1 = 498
        dp_loss_bc = 0
        dp_loss_de = 0
        dp_RA1 = 0
        dp_loss_ef = 0
        g_bc_max = 50
        g_bc_min = g_ab

        cnt1 = 0
        while abs(dp_SA1 + dp_loss_bc + dp_loss_de + dp_RA1 + dp_loss_eb) > 0.01:
            g_bc = (g_bc_max + g_bc_min) / 2
            dp_loss_bc = (s_bc + kr_AHU) * g_bc ** 2
            dp_SA1 = dp_fan(inv_sa1, g_bc, pg_SA1)
            g_eb = g_bc - g_ab
            dp_loss_eb = s_eb * g_eb ** 2 + dp_loss_damper(damp_eb, g_eb)
            # dp_ab + dp_bc + dp_gh = 0
            # dp_ab = dp_loss_ab + dp_loss_damper(damp_ab, g_ab)
            # dp_bc = dp_loss_bc + dp_SA1
            # dp_gh = - dp_loss_ab - dp_loss_damper(damp_ab, g_ab)) - dp_loss_bc - dp_SA1
            # ここでg_ghを求める
            dp_loss_de = 0
            dp_RA1 = 0
            g_gh_max = 25  # EAは風量25㎥/min以上吹くと圧損[Pa]が0になる
            g_gh_min = 0

            cnt2 = 0
            while abs(dp_loss_ab + dp_SA1 + dp_loss_bc + dp_EA1 + dp_loss_gh) > 0.01:
                g_gh = (g_gh_max + g_gh_min) / 2
                dp_EA1 = dp_fan(inv_ea1, g_gh, pg_EA1)
                dp_loss_gh = s_gh * g_gh ** 2
                if dp_loss_ab + dp_SA1 + dp_loss_bc + dp_EA1 + dp_loss_gh > 0:
                    g_gh_min = g_gh
                else:
                    g_gh_max = g_gh
                cnt2 += 1
                if cnt2 > 50:
                    break

            g_de = g_bc - g_gh
            dp_loss_de = s_de * g_de ** 2
            dp_RA1 = dp_fan(inv_ra1, g_de, pg_RA1)
            if dp_SA1 + dp_loss_bc + dp_loss_de + dp_RA1 + dp_loss_eb > 0:
                g_bc_min = g_bc
            else:
                g_bc_max = g_bc
            cnt1 += 1
            if cnt1 > 50:
                break

        g_ef = g_de - g_eb
        dp_loss_ef = s_ef * g_ef ** 2 + dp_loss_damper(damp_ef, g_ef)
        if dp_loss_ab + dp_SA1 + dp_loss_bc + dp_loss_de + dp_RA1 + dp_loss_ef > 0:
            g_ab_min = g_ab
        else:
            g_ab_max = g_ab
        cnt0 += 1
        if cnt0 > 50:
            break

    p_b = dp_loss_ab
    p_c = dp_loss_ab + dp_SA1 + dp_loss_bc
    p_e = dp_loss_ab + dp_SA1 + dp_loss_bc + dp_loss_de + dp_RA1

    [pw_SA1, flag_SA1] = power_fan(g_bc, dp_SA1 / 1000, 1, 1.0262, 2.6395, 0.0004, -0.0011)
    [pw_RA1, flag_RA1] = power_fan(g_de, dp_RA1 / 1000, 1, 1.0262, 2.6395, 0.0004, -0.0011)
    [pw_EA1, flag_EA1] = power_fan(g_gh, dp_EA1 / 1000, 1, 1.0262, 2.6395, 0.0004, -0.0011)

    return cnt0, cnt1, cnt2, g_ab, g_bc, g_gh, g_de, g_ef, g_eb, dp_SA1, dp_RA1, dp_EA1, pw_SA1, pw_EA1, pw_RA1, \
           flag_SA1, flag_RA1, flag_EA1, p_b, p_c, p_e

input_data = pd.read_csv("Input.csv", index_col=0, parse_dates=True)

dataset = []
df_cnt0 = []
df_cnt1 = []
df_cnt2 = []
df_g_ab = []
df_g_bc = []
df_g_gh = []
df_g_de = []
df_g_ef = []
df_g_eb = []
df_dp_SA1 = []
df_dp_RA1 = []
df_dp_EA1 = []
df_pw_SA1 = []
df_pw_EA1 = []
df_pw_RA1 = []
df_flag_SA1 = []
df_flag_RA1 = []
df_flag_EA1 = []
df_p_b = []
df_p_c = []
df_p_e = []

for calstep in tqdm(range(16)):
    inv_sa1 = input_data.iat[calstep, 0]
    inv_ra1 = input_data.iat[calstep, 1]
    inv_ea1 = input_data.iat[calstep, 2]
    damp_ab = input_data.iat[calstep, 3]
    damp_ef = input_data.iat[calstep, 4]
    damp_eb = input_data.iat[calstep, 5]

    [cnt0, cnt1, cnt2, g_ab, g_bc, g_gh, g_de, g_ef, g_eb, dp_SA1, dp_RA1, dp_EA1, pw_SA1, pw_EA1, pw_RA1, \
           flag_SA1, flag_RA1, flag_EA1, p_b, p_c, p_e] = flow_balance(inv_sa1, inv_ra1, inv_ea1, damp_ab, damp_ef, damp_eb)

    dataframe = pd.DataFrame(dataset)
    df_flow = pd.DataFrame(dataset)

    df_cnt0.extend([cnt0])
    df_cnt1.extend([cnt1])
    df_cnt2.extend([cnt2])
    df_g_ab.extend([g_ab])
    df_g_bc.extend([g_bc])
    df_g_gh.extend([g_gh])
    df_g_de.extend([g_de])
    df_g_ef.extend([g_ef])
    df_g_eb.extend([g_eb])
    df_dp_SA1.extend([dp_SA1])
    df_dp_RA1.extend([dp_RA1])
    df_dp_EA1.extend([dp_EA1])
    df_pw_SA1.extend([pw_SA1])
    df_pw_RA1.extend([pw_RA1])
    df_pw_EA1.extend([pw_EA1])
    df_flag_SA1.extend([flag_SA1])
    df_flag_RA1.extend([flag_RA1])
    df_flag_EA1.extend([flag_EA1])
    df_p_b.extend([p_b])
    df_p_c.extend([p_c])
    df_p_e.extend([p_e])

df_flow['cnt0'] = df_cnt0
df_flow['cnt1'] = df_cnt1
df_flow['cnt2'] = df_cnt2
df_flow['g_ab'] = df_g_ab
df_flow['g_bc'] = df_g_bc
df_flow['g_gh'] = df_g_gh
df_flow['g_de'] = df_g_de
df_flow['g_ef'] = df_g_ef
df_flow['g_eb'] = df_g_eb
df_flow['dp_SA1'] = df_dp_SA1
df_flow['dp_RA1'] = df_dp_RA1
df_flow['dp_EA1'] = df_dp_EA1
df_flow['pw_SA1'] = df_pw_SA1
df_flow['pw_RA1'] = df_pw_RA1
df_flow['pw_EA1'] = df_pw_EA1
df_flow['flag_SA1'] = df_flag_SA1
df_flow['flag_RA1'] = df_flag_RA1
df_flow['flag_EA1'] = df_flag_EA1
df_flow['p_b'] = df_p_b
df_flow['p_c'] = df_p_c
df_flow['p_e'] = df_p_e

df_1 = df_flow.iloc[-16:]
df_1[:16].to_csv('Output_3.csv')

