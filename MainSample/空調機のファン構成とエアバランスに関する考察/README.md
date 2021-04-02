### 空調機のファン構成とエアバランスに関するケーススタディ
  
<img src="https://user-images.githubusercontent.com/27459538/113416271-ed2a9f80-93fb-11eb-9f89-d06136d71e81.png" width=60%>  
  
ひとまずダンパはモデル化の対象外（ダクトの圧力損失で模擬する）とし、ファン構成とエアバランスを考える。  
[FlowBalance_1Room_SAFan_RAFan_EAFan.py](https://github.com/ShoheiMiyata/phyvac/blob/main/MainSample/%E7%A9%BA%E8%AA%BF%E6%A9%9F%E3%81%AE%E3%83%95%E3%82%A1%E3%83%B3%E6%A7%8B%E6%88%90%E3%81%A8%E3%82%A8%E3%82%A2%E3%83%90%E3%83%A9%E3%83%B3%E3%82%B9%E3%81%AB%E9%96%A2%E3%81%99%E3%82%8B%E8%80%83%E5%AF%9F/FlowBalance_1Room_SAFan_RAFan_EAFan.py) は1室にSA・RA・EAファンが接続された場合  
[FlowBalance_1Room_SAFan_RAFan_EAFan_Infiltration.py](https://github.com/ShoheiMiyata/phyvac/blob/main/MainSample/%E7%A9%BA%E8%AA%BF%E6%A9%9F%E3%81%AE%E3%83%95%E3%82%A1%E3%83%B3%E6%A7%8B%E6%88%90%E3%81%A8%E3%82%A8%E3%82%A2%E3%83%90%E3%83%A9%E3%83%B3%E3%82%B9%E3%81%AB%E9%96%A2%E3%81%99%E3%82%8B%E8%80%83%E5%AF%9F/FlowBalance_1Room_SAFan_RAFan_EAFan_Infiltration.py) はすき間（上図ij）のある1室にSA・RA・EAファンが接続された場合  
の流量バランス計算を表し、  
[FlowBalance_1Room_SAFan_RAFan_EAFan_Infiltration_PIDbalaning.py](https://github.com/ShoheiMiyata/phyvac/blob/main/MainSample/%E7%A9%BA%E8%AA%BF%E6%A9%9F%E3%81%AE%E3%83%95%E3%82%A1%E3%83%B3%E6%A7%8B%E6%88%90%E3%81%A8%E3%82%A8%E3%82%A2%E3%83%90%E3%83%A9%E3%83%B3%E3%82%B9%E3%81%AB%E9%96%A2%E3%81%99%E3%82%8B%E8%80%83%E5%AF%9F/FlowBalance_1Room_SAFan_RAFan_EAFan_Infiltration_PIDbalancing.py)はファンinvやダクト圧力損失係数をPID制御によって仮想的に調整するプログラムである。流量はファンによる加圧と、ダクトによる圧力損失とが釣り合う点が本プログラムでは算出される。  
    
すき間あり、各ファンのP-Q曲線が以下で同一、圧力損失係数は全て0.5 Pa/(m<sup>3</sup>/min)<sup>2</sup>とした場合、  
<img src="https://user-images.githubusercontent.com/27459538/113414238-860aec00-93f7-11eb-8d3e-32d4adf9698a.png" width=40%>  

`Fan_SA.inv = 1.0, Fan_RA.inv = 1.0, Fan_EA.inv = 1.0`（inv=1.0は周波数比100%（50Hz or 60Hz）を意味する）の時、
```
室内外差圧:  -29.48 Pa
各ダクトの風量(m3/min, 矢印の向きが正)
← 3.24 －－－ RAファン: 10.35 ←－－
          ↓                      ｜
         7.1     　　　   　　 　 室 →EAファン: 10.76
          ｜                        →すき間: -7.68
          ｜                  　 ↑
→ 6.32 －－－→SAファン: 13.43 －－
```
となる。EAファンの引っ張りが強く、室圧が負圧に、流入すきま風が大きい。  
  
***
  
#### エアバランスを下図（VAV空調システムFPT1手順書付属書　図4-0参照）のように調整することを試みる。  
<img src="https://user-images.githubusercontent.com/27459538/113411222-2fe67a80-93f0-11eb-928d-2066b77694a2.png" width=40%>  
  
各種ファンのみを調整すると、`Fan_SA.inv = 0.84, Fan_RA.inv = 0.74, Fan_EA.inv = 0.08`の時に以下のようになる。
```
室内外差圧:  0.0 Pa
各ダクトの風量(m3/min, 矢印の向きが正)
← 3.41 －－－ RAファン: 9.0 ←－－
          ↓                    ｜
         5.59     　　　   　　 室 →EAファン: 1.0
          ｜                      →すき間: 0.0
          ｜                  　↑
→ 4.42 －－－→SAファン: 10.0 －－
```
SAファン風量-EAファン風量=RAファン風量となり、すき間風量がなくなることで、結果として室圧も外気圧と同等になる。  
さらに、外気導入量と余剰排気量を調節するために、ダクトabとefの圧力損失係数を調節すると以下のようになる。
```
室内外差圧:  0.0 Pa
各ダクトの風量(m3/min, 矢印の向きが正)
← 1.99 －－－ RAファン: 9.0 ←－－
          ↓                    ｜
         7.0     　　　   　 　 室 →EAファン: 1.0
          ｜                      →すき間: 0.0
          ｜                  　↑
→ 3.01 －－－→SAファン: 10.0 －－
```
このとき、`Fan_SA.inv = 0.87, Fan_RA.inv = 0.77, Fan_EA.inv = 0.08, abの圧力損失係数:1.67, efの圧力損失係数：2.37`であった。。  
なお、調整は各ファンのinvとab・efの圧力損失係数を仮想的にPI制御しておこなった。
