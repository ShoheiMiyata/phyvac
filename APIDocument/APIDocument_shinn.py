# 2021/2/17 shinn
# APIドキュメント(test)

## バルブのAPIドキュメント

# Valve.f2p(cv_max=800, r=100, vlv=0, g)
# 流量を用いてバルブにより圧力損失を求める
# パラメータ : cv_max :流量係数
#             r :レンジアビリティ。最も弁を閉じたときの流量比の逆数 
#             vlv :バルブ開度(1:全開,0:全閉)
#             g :流量
# 戻り値: dp :バルブによる圧力損失[kPa]
# Error Returns: dp = 0 


# Valve.p2f(cv_max=800, r=100, vlv=0, dp)
# バルブにより圧力損失を用いて流量を求める
# パラメータ : cv_max :流量係数
#             r :レンジアビリティ。最も弁を閉じたときの流量比の逆数 
#             vlv :バルブ開度(1:全開,0:全閉)
#             dp :バルブによる圧力損失[kPa]
# 戻り値: g :流量[m3/min]


# Valve.f2p_co(cv_max=800, r=100, vlv=0)
# 流量を用いてバルブにより圧力損失を求める時の効率を計算する
# パラメータ : cv_max :流量係数
#             r :レンジアビリティ。最も弁を閉じたときの流量比の逆数 
#             vlv :バルブ開度(1:全開,0:全閉)
# 戻り値: np.array



## ポンプのAPIドキュメント

# Pump.f2p(pg=[233,5.9578,-4.95], inv=0, g)
# 流量を用いてポンプにより揚程を求める
# パラメータ : pq :圧力-流量(pg)曲線の係数（切片、一次、二次）
#             inv :回転数比(0.0~1.0)
#             g :流量
# 戻り値: dp :ポンプ揚程[kPa]
# Error Returns: flag = 1 (dp < 0) 
#                

# Pump.f2p_co=(pg=[233,5.9578,-4.95], inv=0)
# 流量を用いてポンプにより揚程を求める時の効率を計算する
# パラメータ : pq :圧力-流量(pg)曲線の係数（切片、一次、二次）
#             inv :回転数比(0.0~1.0)
# 戻り値: 揚程を求める時の効率


# Pump.cal(pg=[233,5.9578,-4.95], eg=[0.0099,0.4174,-0.0508], r_ef=0.8, inv=0,  g)
# 流量がある場合ポンプの消費電力を求める
# パラメータ : pq :圧力-流量(pg)曲線の係数（切片、一次、二次）
#             eq :効率-流量(eg)曲線の係数（切片、一次、二次）
#             r_ef  :定格時の最高効率 rated efficiency
#             inv :回転数比(0.0~1.0)
#             g :流量[m3/min]
# 戻り値: pw :消費電力[kW]
# Error Returns: flag = 1 (dp < 0) dp :ポンプ揚程[kPa]
#                flag = 2(ef < 0) ef: 効率
               
               

## 冷却塔のAPIドキュメント

# CoolingTower.cal(g_w=0, Twin=15, Tda=15, rh=50, inv=0, g_a=10)
# 冷却塔における冷却水出口温度を求める
# パラメータ : g_w :冷却水流量[kg/s]
#             Twin :冷却水入口温度[℃]
#             Tda :外気乾球温度[℃]
#             rh  :外気相対湿度(0~100)
#             g_a :風量[kg/s]
# 戻り値: tout_w :冷却水出口温度[℃]
# Error Returns: flag = 1 (cnt > 30) 


# CoolingTower.f2p(g_w)
# 冷却水流量を用いて揚程を求める
# パラメータ : g_w :冷却水流量[kg/s]
# 戻り値: dp :冷却塔揚程[kPa]


# CoolingTower.f2p_co()
# 冷却水流量を用いて揚程を求める時の効率を計算する
# パラメータ : kr=1.0
# 戻り値: [0,0,-self.kr]






