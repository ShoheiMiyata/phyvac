"""
@author: akrnmr
"""
# SA1       給気ファン
# RA1       還気ファン
# EA1       (室からの)排気ファン
# AHU1      空調機
# DAMP1     DAMP_ab
# DAMP2     DAMP_ef
# DAMP3     DAMP_eb

import 3Dampers_3Fans_phyvac as pv

# 機器の定義
AHU1 = pv.AHU_simple(kr=1.0)
DAMP1 = pv.Damper()
DAMP2 = pv.Damper()
DAMP3 = pv.Damper()
SA1 = pv.Fan(pg=[494, -1.8337, 0.0372, -0.0005, 0], inv=1.0)         # eg=[-0.0166, 0.0399, -0.0008],
RA1 = pv.Fan(pg=[318, -1.5863, 0.2251, -0.023, 0.0002], inv=1.0)     # eg=[0, 0.0111, -5E-05]
EA1 = pv.Fan(pg=[176.62, -1.5863, 0.2251, -0.023, 0.0002], inv=1.0)  # eg=[-0.0166, 0.0399, -0.0008]

# 管抵抗の定義
# Branch30  空気側の枝
Branch_ab = pv.Branch30(s=-0.005777388)   # 今回のsは[Pa/(m3/min)^2]なので圧損の単位はPa
Branch_bc = pv.Branch30(s=-0.9886798854)  # AHUの抵抗を-1.0として加えている
Branch_de = pv.Branch30(s=-0.0921395376)
Branch_eb = pv.Branch30(s=-0.0031888728)
Branch_ef = pv.Branch30(s=-3.5176416)
Branch_gh = pv.Branch30(s=-0.01)

# 単室流量計算
# 空気系


def flow_balance(damp1, damp2, damp3):
    p_atm = 101300  # [Pa]
    g_ab = g_bc = g_de = g_eb = g_ef = g_gh = 0
    Branch_ab.dp = Branch_bc.dp = Branch_de.dp = Branch_eb.dp = Branch_ef.dp = Branch_gh.dp = 0
    DAMP1.dp = DAMP2.dp = DAMP3.dp = 0
    SA1.dp = 498
    RA1.dp = EA1.dp = 0
    g_ab_max = 50
    g_ab_min = 0

    cnt0 = 0
    while abs(Branch_ab.dp + DAMP1.dp + SA1.dp + Branch_bc.dp + Branch_de.dp + RA1.dp + Branch_ef.dp + DAMP2.dp) > 0.01:
        g_ab = (g_ab_max + g_ab_min) / 2
        Branch_ab.f2p(g=g_ab)
        DAMP1.loss(g=g_ab, damp=damp1)
        g_bc_max = 50
        g_bc_min = g_ab

        cnt1 = 0
        while abs(SA1.dp + Branch_bc.dp + Branch_de.dp + RA1.dp + Branch_eb.dp + DAMP3.dp) > 0.01:
            g_bc = (g_bc_max + g_bc_min) / 2
            SA1.f2p(g=g_bc)
            Branch_bc.f2p(g=g_bc)
            g_eb = g_bc - g_ab
            Branch_eb.f2p(g=g_eb)
            DAMP3.loss(g=g_eb, damp=damp3)
            g_gh_max = g_bc
            g_gh_min = 0

            cnt2 = 0
            while abs(Branch_ab.dp + DAMP1.dp + SA1.dp + Branch_bc.dp + EA1.dp + Branch_gh.dp) > 0.01:
                g_gh = (g_gh_max + g_gh_min) / 2
                Branch_gh.f2p(g=g_gh)
                EA1.f2p(g=g_gh)
                if Branch_ab.dp + DAMP1.dp + SA1.dp + Branch_bc.dp + EA1.dp + Branch_gh.dp > 0:
                    g_gh_min = g_gh
                else:
                    g_gh_max = g_gh
                cnt2 += 1
                if cnt2 > 50:
                    break

            g_de = g_bc - g_gh
            Branch_de.f2p(g=g_de)
            RA1.f2p(g=g_de)
            if SA1.dp + Branch_bc.dp + Branch_de.dp + RA1.dp + Branch_eb.dp + DAMP3.dp > 0:
                g_bc_min = g_bc
            else:
                g_bc_max = g_bc
            cnt1 += 1
            if cnt1 > 50:
                break

        g_ef = g_de - g_eb
        Branch_ef.f2p(g=g_ef)
        DAMP2.loss(g=g_ef, damp=damp2)
        if Branch_ab.dp + DAMP1.dp + SA1.dp + Branch_bc.dp + Branch_de.dp + RA1.dp + Branch_ef.dp + DAMP2.dp > 0:
            g_ab_min = g_ab
        else:
            g_ab_max = g_ab
        cnt0 += 1
        if cnt0 > 50:
            break

    p_b = p_atm + Branch_ab.dp + DAMP1.dp
    p_c = p_atm + Branch_ab.dp + DAMP1.dp + SA1.dp + Branch_bc.dp
    p_e = p_atm + Branch_ab.dp + DAMP1.dp + SA1.dp + Branch_bc.dp + Branch_de.dp + RA1.dp

    return g_ab, g_bc, g_gh, g_de, SA1.dp, RA1.dp, EA1.dp, p_b, p_c, p_e

[g_ab, g_bc, g_gh, g_de, dp_SA1, dp_RA1, dp_EA1, p_b, p_c, p_e] = flow_balance(1,1,1)
print("g_ab=", g_ab, "g_bc=", g_bc, "g_gh=", g_gh, "g_de=", g_de,
      "dp_SA1=", dp_SA1, "dp_RA1=", dp_RA1, "dp_EA1=", dp_EA1, "p_b=", p_b, "p_c=", p_c, "p_e=", p_e)
