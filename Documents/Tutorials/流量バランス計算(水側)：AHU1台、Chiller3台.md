## 流量バランス計算：AHU1台、Chiller3台  
システム図（左：元の構成→右：流量バランス計算のために枝の数が少なくなるようBranchを定義）  
<img src="https://user-images.githubusercontent.com/27459538/112785753-b2d5a100-908f-11eb-8c4f-27d558c70790.png" width=80%>

  
## コード例 - FlowBalance_1AHU_3Chillers.py
コード全体は[こちら](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/Tutorials/FlowBalance_1AHU_3Chillers.py)にアップロードされています。  
  
まず最初に、phyvacをインポートします。
```
import phyvac as pv
``` 
### 機器の定義
`AHU`:air handling units, `Vlv_AHU`: AHU用の弁, `CP1`: Chiller1用の冷水ポンプ  
モジュールの初期値が対象機器において不適切な場合、特性パラメータを適宜入力します。ここでは簡略のためChillerモジュールは使いません。
```
# 機器の定義
AHU = pv.AHU_simple(kr=2.0)
Vlv_AHU = pv.Valve(cv_max=800,r=100)
CP1 = pv.Pump(pg=[233.9,5.9578,-4.460], eg=[0.009964,0.4174,-0.0508])
CP2 = pv.Pump(pg=[233.9,5.9578,-4.460], eg=[0.009964,0.4174,-0.0508])
CP3 = pv.Pump(pg=[233.9,5.9578,-4.460], eg=[0.009964,0.4174,-0.0508])
```
### 枝の定義  
下図の配管ループは2つの枝（branch）とみなすことができます。 `Branch_aAHUb`が点aからAHUを通り点bまで（[Branch01](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.Branch01_JP.md)）、`Branch_bChiller1a`が点bからChiller1を通り点aまで（[Branch10](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/pv.Branch10_JP.md)）の枝に分けられます。  
流量バランス計算を行うためには、運転時に常に流量が生じる枝(`Branch_aAHUb`)を設定する必要があります。これは配管網が複雑になっても同様です。 
```
# 枝の定義
Branch_aAHUb = pv.Branch01(Vlv_AHU, kr_eq=AHU.kr, kr_pipe=3.0)
Branch_bChiller1a = pv.Branch10(pump=CP1, kr_eq=10.0, kr_pipe=7.0)
Branch_bChiller2a = pv.Branch10(pump=CP2, kr_eq=10.0, kr_pipe=7.0)
Branch_bChiller3a = pv.Branch10(pump=CP3, kr_eq=10.0, kr_pipe=7.0)
```
### 弁開度・ポンプinvの入力
ここでは制御を省いているため、手動で弁開度とポンプinvを入力します。制御機器の状態から、流量が全て算出される点が流量バランス計算の特徴です。  
`Vlv_AHU.vlv`: Vlv_AHUの弁開度。0が全閉、1が全開, `CP1.inv`: CP1のinv周波数比。0が停止、1が定格値（関東だと50Hz）  
```
Vlv_AHU.vlv = 0.7
CP1.inv = 0.7
CP2.inv = 0.7
CP3.inv = 0.7
```
### 流量バランス計算  
まず、運転時に流量が常に生じる枝(`Branch_aAHUb`)の最小流量(`g_min = 0.0`)と最大流量(`g_max = 20.0`)を設定します。また、収束判定用の変数に適当な値を与えます(`g_eva = 10.0`)。  
while文では、まず最初に`Branch_aAHUb`用の流量を仮定します(`g = (g_max + g_min) / 2`, 平均をとるゆえに二分法と呼ばれます)。
```
g_min = 0.0
g_max = 20.0
g_eva = 10.0
cnt = 0
while(g_eva > 0.01)or(g_eva < -0.01):
    cnt += 1
    g = (g_max + g_min) / 2
```
次に、点aと点bの差圧を算出します(`dp1 = Branch_aAHUb.f2p(g)`)。そして、`Branch_bchiller1a`の流量を先ほど得られた`dp1`から算出します(`Branch_bChiller1a.p2f(-dp1)`)。  
この時、`Branch_bChiller1a.p2f()`の入力値には、dp1ではなく-dp1とする点に注意してください。これは、`Branch_aAHUb`での圧力損失(`dp1`)と、`Branch_bChiller1a`での加圧分(`-dp1`)がつり合い、a-AHU-b-Chiller1-aのループにおいて圧力的にバランスすることを意味します。
収束判定用の変数`g_eva`は、`Branch_aAHUb`と、`Branch_bChiller1a`, `Branch_bChiller2a`, `Branch_bChiller3a`の合計流量との差です。このが0に近づく（収束する）ことは、点aまたは点bにおいて、流量的に流出入がバランスすることを意味します。  
`g_eva`が0より大きい場合、`g_max`を再設定し、そうでない場合は`g_min`を再設定します。  
```
    dp1 = Branch_aAHUb.f2p(g)
    Branch_bChiller1a.p2f(-dp1)
    Branch_bChiller2a.p2f(-dp1)
    Branch_bChiller3a.p2f(-dp1)
    g_eva = Branch_aAHUb.g - Branch_bChiller1a.g - Branch_bChiller2a.g - Branch_bChiller3a.g
    if g_eva > 0:
        g_max = g
    else:
        g_min = g
    if cnt > 30:
        break
```
なお、cntは収束計算が適切に行われているか判定する変数です。cnt=31となっている場合、`g_max = g`と`g_min = g`を入れ替えるなど対処が必要です。  
  
```
print(cnt, Branch_aAHUb.g, Branch_bChiller1a.g, Branch_bChiller2a.g, Branch_bChiller3a.g)
```
> 13 2.46826171875 0.8230025426795617 0.8230025426795617 0.8230025426795617
  
```
Vlv_AHU.vlv = 0.8
CP1.inv = 0.8
CP2.inv = 0.7
CP3.inv = 0.65
...
print(cnt, Branch_aAHUb.g, Branch_bChiller1a.g, Branch_bChiller2a.g, Branch_bChiller3a.g)
```
> 13 3.14208984375 1.68956191325158 1.021240362268994 0.43213803391962036
  
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


