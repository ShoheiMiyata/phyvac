# 熱源システムのシステムシミュレーションプログラム
# main文

import pandas as pd
import time
import phyvac as pv
from tqdm import tqdm
import copy
import numpy as np

# 1/25 冷却水温度低下で冷凍機が停止した際の制御ロジックは？
# CP3バイパス弁制御の導入

start = time.time()

# 入力値の読み込み
input_data = pd.read_csv("Input15min_20190707_0713.csv",index_col=0,parse_dates=True)
# input_data = pd.read_csv("Input15min_2019.csv",index_col=0,parse_dates=True)
input_data = input_data.resample('1min').interpolate()
# 出力データフレームの作成
output_data = input_data.drop(input_data.columns[[0,1,2,3,4]], axis=1)
output_data = output_data.assign(AHU1_g=0.0, AHU1_tin=0.0, AHU1_tout=0.0, CP3_inv=0.0,\
                                 Unit_Num_CP3_num=0.0, TR1_tin_ch=0.0, TR1_tout_ch_sv=0.0,\
                                 TR1_tout_ch=0.0, CP1_g_sv=0.0, CP1_g=0.0, CP1_inv=0.0,\
                                 TR1__tin_cd_ll=0.0, TR1_tin_cd=0.0, TR1_tout_cd=0.0,\
                                 CDP1_g_sv=0.0, CDP1_g=0.0, CDP1_inv=0.0, Vlv_CDP1_tin_sv=0.0,\
                                 Vlv_CDP1_vlv=0.0, TR2_tin_ch=0.0, TR2_tout_ch_sv=0.0,\
                                 TR2_tout_ch=0.0, CP2_g_sv=0.0, CP2_g=0.0, CP2_inv=0.0,\
                                 TR2_tin_cd_ll=0.0, TR2_tin_cd=0.0, TR2_tout_cd=0.0,\
                                 CDP2__g_sv=0.0, CDP2_g=0.0, CDP2_inv=0.0, Vlv_CDP1__tin_sv=.00,\
                                 Vlv_CDP2_vlv=0.0, t_wb=0.0, CT__tin_w=0.0, CT_tout_sv=0.0,\
                                 CT_tout_w=0.0, CT_inv=0.0, CP3_pw_all=0.0,TR1_pw=0.0, CP1_pw=0.0, \
                                 CDP1_pw=0.0, TR2_pw=0.0, CP2_pw=0.0, CDP2_pw=0.0, CT_pw=0.0)

# 機器の定義
AHU1 = pv.AHU_simple(kr=2.0)
Vlv_AHU = pv.Valve(cv_max=800,r=100)
Vlv_Bypass = pv.Valve(cv_max=800,r=100)
Vlv_CP3 = pv.Valve(cv_max=1600,r=100)
Vlv_CDP1 = pv.Valve(cv_max=1600,r=100)
Vlv_CDP2 = pv.Valve(cv_max=1600,r=100)
CP1 = pv.Pump(pg=[233.9,5.9578,-4.460], eg=[0.009964,0.4174,-0.0508])
CP2 = pv.Pump(pg=[233.9,5.9578,-4.460], eg=[0.009964,0.4174,-0.0508])
CP3 = pv.Pump(pg=[469.6,17.50,-12.39], eg=[0.01093,0.4411,-0.06426])
CDP1 = pv.Pump(pg=[338.2,-2.499,-1.507], eg=[0.002915,0.2131,-0.01476])
CDP2 = pv.Pump(pg=[338.2,-2.499,-1.507], eg=[0.002915,0.2131,-0.01476])
TR1 = pv.Chiller(spec_table=pd.read_csv("chiller_spec_table.csv",encoding="SHIFT-JIS",header=None))
TR2 = pv.Chiller(spec_table=pd.read_csv("chiller_spec_table.csv",encoding="SHIFT-JIS",header=None))
CT = pv.CoolingTower(kr=2.0, ua=143000)

# 枝の定義
Branch_ab = pv.Branch01(Vlv_AHU, kr_eq=AHU1.kr, kr_pipe=3.0)
Branch_ca = pv.Branch11(valve=Vlv_CP3, pump=CP3, kr_pipe_pump=10.0, kr_pipe_valve=0.3)
Branch_cb = pv.Branch01(valve=Vlv_Bypass, kr_eq=0, kr_pipe=6.0)
Branch_bTR1c = pv.Branch10(pump=CP1, kr_eq=TR1.kr_ch, kr_pipe=10.0)
Branch_bTR2c = pv.Branch10(pump=CP2, kr_eq=TR2.kr_ch, kr_pipe=10.0)
Branch_de = pv.Branch00(kr_pipe=1, kr_eq=CT.kr, head_act = 0.0) 
Branch_eTR1d = pv.Branch12(valve=Vlv_CDP1, pump=CDP1, kr_eq=TR1.kr_cd, kr_pipe=1.0, kr_pipe_bypass=0.5)
Branch_eTR2d = pv.Branch12(valve=Vlv_CDP2, pump=CDP2, kr_eq=TR2.kr_cd, kr_pipe=1.0, kr_pipe_bypass=0.5)

# 制御の定義
PID_AHU_Vlv = pv.PID(kp=0.04, ti=400)
PID_Bypass_Vlv = pv.PID(kp=0.06, ti=20)
PID_CP1 = pv.PID(kp=0.001, ti=400, a_min=0.4)
PID_CP2 = pv.PID(kp=0.02, ti=300, a_min=0.4)
PID_CP3 = pv.PID(kp=0.002, ti=30, a_min=0.4)
PID_CDP1 = pv.PID(kp=0.05, ti=200, a_min=0.4)
PID_CDP2 = pv.PID(kp=0.05, ti=200, a_min=0.4)
PID_CDP1_Vlv = pv.PID(kp=0.002, ti=200)
PID_CDP2_Vlv = pv.PID(kp=0.002, ti=200)
PID_CT = pv.PID(kp=0.005, ti=600, kg=-1)
Unit_Num_TR = pv.Unit_Num_CC(thre_up_g=[3.145*0.8],thre_down_g=[3.145*0.6],thre_up_q=[2000],thre_down_q=[1600])
Unit_Num_CP3 = pv.Unit_Num(thre_up=[1.0, 1.8],thre_down=[0.8, 1.6])

# 設定値演算式定義
# 冷凍機台数制御閾値
def cal_num_TR_thre_q(TR_tin_cd):
    # 冷却水温度32℃で最適負荷範囲60-90%
    # 冷却水温度12℃で最適負荷範囲30-50%
    ll = 0.3 + (TR_tin_cd-12)/20*0.3
    if ll > 0.6:
        ll = 0.6
    elif ll < 0.3:
        ll = 0.3
    
    hl = 0.5 + (TR_tin_cd-12)/20*0.4
    if hl > 0.9:
        hl = 0.9
    elif hl < 0.5:
        hl = 0.5
        
    return [ll, hl]

# 冷却水ポンプ流量設定値
def cal_sv_CDP_g(t_wb,lf,wb_low=4,wb_high=26,g_wb_low0=0.3,g_wb_high0=0.375,g_wb_low100=0.8,g_wb_high100=1.0,sv_min=0.45):
    # t_da:外気乾球温度, rh:外気相対湿度, lf:冷凍機負荷率
    # wb_low:Lo側WB, wb_high:Hi側WB, g_wb_low0:負荷0%時WB_low流量比(0.0~1.0), g_wb_high0:負荷0%時WB_high流量比(0.0~1.0)
    # g_wb_low100:負荷100%時WB_low流量比(0.0~1.0), g_wb_high100:負荷100%時WB_high流量比(0.0~1.0)
    y1 = lf*(g_wb_low100-g_wb_low0)+g_wb_low0
    y2 = lf*(g_wb_high100-g_wb_high0)+g_wb_high0
    sv = y1 + (y2-y1)/(wb_high-wb_low)*(t_wb-wb_low)
    if sv > 1:
        sv = 1
    elif sv < sv_min:
        sv = sv_min
    
    return sv


# 冷却塔冷却水出口温度設定値
def cal_sv_CT_tout(t_wb, dt_wb=4.0, sv_min=7.0):
    sv = t_wb + 4
    if sv < sv_min:
        sv = sv_min
        
    return sv


# for calstep in tqdm(range(24*60*(365+6))):
for calstep in tqdm(range(24*60*(14))):

    g_load = input_data.iat[calstep,0]        # 負荷流量[m3/min]
    q_load = input_data.iat[calstep,1]        # 負荷熱量[GJ/min]
    t_supply_sv = input_data.iat[calstep,2]   # 供給温度設定値['C]
    t_da = input_data.iat[calstep,3]          # 外気乾球温度['C]
    rh = input_data.iat[calstep,4]            # 外気相対湿度[%](0~100)
    t_wb = pv.tda_rh2twb(t_da, rh)
    
    
    # 設定値演算
    CT_tout_sv = cal_sv_CT_tout(t_wb=t_wb)
    TR1_tin_cd_ll = t_supply_sv + 5 # 冷凍機冷却水入口温度下限値
    TR2_tin_cd_ll = t_supply_sv + 5
    [Num_TR_thre_down_q, Num_TR_thre_up_q] = cal_num_TR_thre_q(TR1.tin_cd)
    # 台数制御
    Unit_Num_TR.thre_down_q = [Num_TR_thre_down_q*TR1.q_ch_d]
    Unit_Num_TR.thre_up_q = [Num_TR_thre_up_q*TR1.q_ch_d]
    Unit_Num_TR.control(g=Vlv_AHU.g, q=TR1.q_ch+TR2.q_ch)
    Unit_Num_CP3.control(Vlv_AHU.g)
    
    # 制御
    Vlv_AHU.vlv = PID_AHU_Vlv.control(sv=g_load,mv=Vlv_AHU.g)
    Vlv_Bypass.vlv = 0.7    
    CP3.inv = PID_CP3.control(sv=70,mv=-(Branch_ab.dp))
    Vlv_CP3.vlv = 0
    
    if Unit_Num_TR.num == 1:
        CP1_g_sv = g_load*1.1
        CP2_g_sv = 0
        CDP1_g_sv = cal_sv_CDP_g(t_wb=t_wb, lf=TR1.lf)*TR1.g_cd_d
        CDP2_g_sv = 0 
        CP1.inv = PID_CP1.control(sv=CP1_g_sv,mv=CP1.g)
        CP2.inv = 0
        CDP1.inv = PID_CDP1.control(sv=CDP1_g_sv, mv=CDP1.g)
        CDP2.inv = 0
        if TR1.tin_cd > TR1_tin_cd_ll:
            Vlv_CDP1.vlv = 0
        else:
            Vlv_CDP1.vlv = PID_CDP1_Vlv.control(sv=TR1_tin_cd_ll, mv=TR1.tin_cd)
        Vlv_CDP2.vlv = 0
    elif Unit_Num_TR.num == 2:
        CP1_g_sv = g_load*0.55
        CP2_g_sv = g_load*0.55
        CDP1_g_sv = cal_sv_CDP_g(t_wb=t_wb, lf=TR1.lf)*TR1.g_cd_d
        CDP2_g_sv = cal_sv_CDP_g(t_wb=t_wb, lf=TR2.lf)*TR2.g_cd_d
        CP1.inv = PID_CP1.control(sv=g_load*0.55,mv=CP1.g)
        CP2.inv = PID_CP2.control(sv=g_load*0.55,mv=CP2.g)
        CDP1.inv = PID_CDP1.control(sv=CDP1_g_sv, mv=CDP1.g)
        CDP2.inv = PID_CDP2.control(sv=CDP2_g_sv, mv=CDP2.g)
        if TR1.tin_cd > TR1_tin_cd_ll:
            Vlv_CDP1.vlv = 0
        else:
            Vlv_CDP1.vlv = PID_CDP1_Vlv.control(sv=TR1_tin_cd_ll, mv=TR1.tin_cd)
            
        if TR2.tin_cd > TR2_tin_cd_ll:
            Vlv_CDP2.vlv = 0
        else:
            Vlv_CDP2.vlv = PID_CDP2_Vlv.control(sv=TR2_tin_cd_ll, mv=TR2.tin_cd)

    CT.inv = PID_CT.control(sv=CT_tout_sv,mv=CT.tout_w)
    
    # 流量計算
    # 冷水系
    g_eva = 10
    g_max = 20
    g_min = 0
    cnt = 0
    while(g_eva > 0.01)or(g_eva < -0.01):
        cnt += 1
        g = (g_max + g_min) / 2
        p1 = Branch_ab.f2p(g)
        p2 = Branch_ca.f2p(g)
        Branch_cb.p2f(p1+p2)
        Branch_bTR1c.p2f(-p1-p2)
        Branch_bTR2c.p2f(-p1-p2)
        g_eva = Branch_ab.g + Branch_cb.g - Branch_bTR1c.g - Branch_bTR2c.g
        if g_eva > 0:
            g_max = g
        else:
            g_min = g
        if cnt > 30:
            break
    
    # 冷却水系
    g_eva = 10
    g_max = 20
    g_min = 0
    cnt = 0
    while(g_eva > 0.01)or(g_eva < -0.01):
        cnt += 1
        g = (g_max + g_min) / 2
        p1 = Branch_de.f2p(g)
        Branch_eTR1d.p2f(-p1)
        Branch_eTR2d.p2f(-p1)
        g_eva = Branch_de.g - Branch_eTR1d.g - Branch_eTR2d.g
        if g_eva > 0:
            g_max = g
        else:
            g_min = g
        if cnt > 30:
            break
    
    # 機器状態計算 
    # 前時刻の温度を保存
    AHU1_0 = copy.deepcopy(AHU1)
    TR1_0 = copy.deepcopy(TR1)
    TR2_0 = copy.deepcopy(TR2)
    CT_0 = copy.deepcopy(CT)
    
    # 現時刻の温度・消費電力計算
    AHU1.cal(g=Vlv_AHU.g,tin=TR1_0.tout_ch,q_load=q_load)
    if CDP1.g+CDP2.g>0:
        TR_tin_cd = (CT_0.tout_w*(CDP1.g+CDP2.g-Vlv_CDP1.g-Vlv_CDP2.g)\
                     +TR1_0.tout_cd*Vlv_CDP1.g+TR2_0.tout_cd*Vlv_CDP2.g)/(CDP1.g+CDP2.g)
        CT_tin_w = (TR1_0.tout_cd*Branch_eTR1d.g+TR2_0.tout_cd*Branch_eTR2d.g)/(Branch_eTR1d.g+Branch_eTR2d.g)
    if CP1.g+CP2.g>0 and Vlv_Bypass.g+AHU1.g>0:
        tin_ch = ((TR1_0.tout_ch*CP1.g+TR2_0.tout_ch*CP2.g)/(CP1.g+CP2.g)*\
                  Vlv_Bypass.g+AHU1_0.tout*AHU1.g)/(Vlv_Bypass.g+AHU1.g)
    TR1.cal(tout_ch_sv=t_supply_sv, tin_ch=tin_ch, g_ch=CP1.g, tin_cd=TR_tin_cd, g_cd=CDP1.g)
    TR2.cal(tout_ch_sv=t_supply_sv, tin_ch=tin_ch, g_ch=CP2.g, tin_cd=TR_tin_cd, g_cd=CDP2.g)
    CP1.cal()
    CP2.cal()
    CP3.cal()
    CDP1.cal()
    CDP2.cal()  
    # print(Branch_de.g, Branch_de.dp, Branch_de.kr_pipe, Branch_de.kr_eq)
    CT.cal(g_w=Branch_eTR1d.g+Branch_eTR2d.g, Twin=CT_tin_w, Tda=t_da, rh=rh)
    

    
    output_data.iloc[calstep] = np.array([[AHU1.g, AHU1.tin, AHU1.tout, CP3.inv,\
                                           Unit_Num_CP3.num, TR1.tin_ch, TR1.tout_ch_sv,\
                                           TR1.tout_ch, CP1_g_sv, CP1.g, CP1.inv, \
                                           TR1_tin_cd_ll, TR1.tin_cd, TR1.tout_cd, \
                                           CDP1_g_sv, CDP1.g, CDP1.inv, TR1_tin_cd_ll,\
                                           Vlv_CDP1.vlv, TR2.tin_ch, TR2.tout_ch_sv,\
                                           TR2.tout_ch, CP2_g_sv, CP2.g, CP2.inv,\
                                           TR2_tin_cd_ll, TR2.tin_cd, TR2.tout_cd,\
                                           CDP2_g_sv, CDP2.g, CDP2.inv, TR1_tin_cd_ll,\
                                           Vlv_CDP2.vlv, t_wb, CT.tin_w, CT_tout_sv,\
                                           CT.tout_w, CT.inv, CP3.pw*Unit_Num_CP3.num,\
                                           TR1.pw, CP1.pw, CDP1.pw, TR2.pw, CP2.pw, CDP2.pw, CT.pw]])
                                           


output_data = output_data.resample('15min').mean()
output_data = output_data['2019-07-07 00:00' : '2019-07-13 23:45']
output_data.to_csv('result2019_15min.csv')

print(time.time() - start)

