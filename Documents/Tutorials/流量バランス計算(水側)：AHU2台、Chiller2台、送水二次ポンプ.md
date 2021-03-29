## 流量バランス計算：AHU2台、Chiller2台、送水二次ポンプ  
システム図（左：元の構成→右：流量バランス計算のために枝の数が少なくなるようBranchを定義）  
<img src="https://user-images.githubusercontent.com/27459538/112785994-3e4f3200-9090-11eb-8604-f77e7ce6c840.png" width=80%>

  
## コード例 - FlowBalance_2AHU_2Chillers_SecondaryPump.py
コード全体は[こちら](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/Tutorials/FlowBalance_2AHU_2Chillers_SecondaryPump.py)にアップロードされています。  
利用するモジュール：[Branch01](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.Branch01_JP.md), [Branch10](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.Branch10_JP.md), [Branch11](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.Branch11_JP.md)
  
まず最初に、phyvacをインポートします。
```
import phyvac as pv
``` 
### 機器の定義
`AHU`: air handling units, `Vlv_AHU`: AHU用の弁, `CP`: 冷水ポンプ  
モジュールの初期値が対象機器において不適切な場合、特性パラメータを適宜入力します。ここでは簡略のためChillerモジュールは使いません。
```
# 機器の定義
AHU1 = pv.AHU_simple(kr=2.0)
Vlv_AHU1 = pv.Valve(cv_max=800,r=100)
AHU2 = pv.AHU_simple(kr=2.0)
Vlv_AHU2 = pv.Valve(cv_max=800,r=100)
CP1 = pv.Pump(pg=[233.9,5.9578,-4.460], eg=[0.009964,0.4174,-0.0508])
CP2 = pv.Pump(pg=[233.9,5.9578,-4.460], eg=[0.009964,0.4174,-0.0508])
CP3 = pv.Pump(pg=[233.9,5.9578,-4.460], eg=[0.009964,0.4174,-0.0508])
Vlv_CP3 = pv.Valve(cv_max=800,r=100)
```
### 枝の定義  
下図の配管ループは2つの枝（branch）とみなすことができます。 `Branch_aCP3b`が点aからCP3を通り点bまで（[Branch11](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.Branch11_JP.md)）、`Branch_bAHU1c`が点bからAHU1を通り点cまで（[Branch01](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.Branch01_JP.md)）、`Branch_cChiller1a`が点cからChiller1を通り点aまで（[Branch10](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.Branch10_JP.md)）の枝に大別できます。  
流量バランス計算を行うためには、運転時に常に流量が生じる枝(`Branch_aCP3b`)を設定する必要があります。これは配管網が複雑になっても同様です。 
```
# 枝の定義
BranchaCP3b = pv.Branch11(valve=Vlv_CP3, pump=CP3, kr_pipe_pump=3.0, kr_pipe_valve=4.0)
Branch_bAHU1c = pv.Branch01(Vlv_AHU1, kr_eq=AHU1.kr, kr_pipe=3.0)
Branch_bAHU2c = pv.Branch01(Vlv_AHU2, kr_eq=AHU2.kr, kr_pipe=3.0)
Branch_cChiller1a = pv.Branch10(pump=CP1, kr_eq=10.0, kr_pipe=7.0)
Branch_cChiller2a = pv.Branch10(pump=CP2, kr_eq=10.0, kr_pipe=7.0)
```
### 弁開度・ポンプinvの入力
ここでは制御を省いているため、手動で弁開度とポンプinvを入力します。制御機器の状態から、流量が全て算出される点が流量バランス計算の特徴です。  
`Vlv_AHU1.vlv`: Vlv_AHU1の弁開度。0が全閉、1が全開, `CP1.inv`: CP1のinv周波数比。0が停止、1が定格値（関東だと50Hz）  
```
Vlv_AHU1.vlv = 0.6
Vlv_AHU2.vlv = 0.8
CP1.inv = 0.7
CP2.inv = 0.7
CP3.inv = 0.6
Vlv_CP3.vlv = 0.0
```
### 流量バランス計算  
まず、運転時に流量が常に生じる枝(`Branch_aCP3b`)の最小流量(`g1_min = 0.0`)と最大流量(`g1_max = 20.0`)を設定します。また、収束判定用の変数に適当な値を与えます(`g1_eva = 10.0`)。  
while文では、まず最初に`Branch_aCP3b`用の流量を仮定します(`g1 = (g1_max + g1_min) / 2`, 平均をとるゆえに二分法と呼ばれます)。
```
g1_min = 0.0
g1_max = 20.0
g1_eva = 10.0
cnt1 = 0
while(g1_eva > 0.01)or(g1_eva < -0.01):
    cnt1 += 1
    g1 = (g1_max + g1_min) / 2
```
今回はg1の仮定のみではAHUとChillerの分岐の流量バランスを解くことができません。そのため、さらにもう一回仮定を与える必要があります。そこで、`Branch_bAHU1c`または`Branch_bAHU2c`の圧力差を`dp2`として仮定します。    
`BranchaCP3b`の圧力差`dp1`は仮定した`g1`から求められます。次に、`dp1`、`dp2`から、`Branch_bChiller1a`または`Branch_bChiller2a`の圧力差は`-dp1-dp2`と分かります。  
そこで、点cにおける流出入の流量が等しくなるよう収束計算を行います（評価関数`dp2_eva = Branch_bAHU1c.g + Branch_bAHU2c.g - Branch_cChiller1a.g - Branch_cChiller2a.g`）。  
```
    dp1 = BranchaCP3b.f2p(g1)
    dp2_min = -300.0
    dp2_max = 0.0
    dp2_eva = 100.0
    cnt2 = 0
    while(dp2_eva > 0.01)or(dp2_eva < -0.01):
        cnt2 += 1
        dp2 = (dp2_max + dp2_min) / 2
        Branch_bAHU1c.p2f(dp2)
        Branch_bAHU2c.p2f(dp2)
        Branch_cChiller1a.p2f(-dp1-dp2)
        Branch_cChiller2a.p2f(-dp1-dp2)
        dp2_eva = Branch_bAHU1c.g + Branch_bAHU2c.g - Branch_cChiller1a.g - Branch_cChiller2a.g
        if dp2_eva > 0:
            dp2_min = dp2
        else:
            dp2_max = dp2
        if cnt2 > 30:
            break
```
なお、cnt2は収束計算が適切に行われているか判定する変数です。cnt2=31となっている場合、`dp2_max = dp2`と`dp2_min = dp2`を入れ替えるなど対処が必要です。  
この段階で、点bから点cを通り、点aまでのネットワークにおいて、出入口圧力差が-dp1であり、かつ点cにおける出入流量のバランスがとれている各枝の流量が得られています。  
最後に、点bでの出入流量がバランスするように収束計算をおこないます（評価関数`g1_eva = BranchaCP3b.g - Branch_cChiller1a.g - Branch_cChiller2a.g`）。
  
```
    g1_eva = BranchaCP3b.g - Branch_cChiller1a.g - Branch_cChiller2a.g
    if g1_eva > 0:
        g1_max = g1
    else:
        g1_min = g1
    if cnt1 > 30:
        break
    
print(cnt1, cnt2, BranchaCP3b.g, Branch_bAHU1c.g, Branch_bAHU2c.g, Branch_cChiller1a.g, Branch_cChiller2a.g)
```
> 結果
> 13 2.46826171875 0.8230025426795617 0.8230025426795617 0.8230025426795617
  
```
Vlv_AHU.vlv = 0.8
CP1.inv = 0.8
CP2.inv = 0.7
CP3.inv = 0.65
...
print(cnt, Branch_aAHUb.g, Branch_bChiller1a.g, Branch_bChiller2a.g, Branch_bChiller3a.g)
```
> 11 7 3.583984375 1.2389662697778567 2.3485503638523513 1.791632257411038 1.791632257411038
  
```
Vlv_AHU.vlv = 0.8
CP1.inv = 0.8
CP2.inv = 0.7
CP3.inv = 0.6
...
print(cnt, Branch_aAHUb.g, Branch_bChiller1a.g, Branch_bChiller2a.g, Branch_bChiller3a.g)
```
> 9 3.0078125 1.804502107933294 1.2062172022095325 0.0  
> 並列ポンプのinvが大きく異なると、invの小さいポンプの圧力が不足し、流量が生じないという計算結果となる。


