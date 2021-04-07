### 空調機のファン構成とエアバランスに関するケーススタディ
  
<img src="https://user-images.githubusercontent.com/27459538/113809880-076dd000-97a4-11eb-94dc-24da9b961b19.png" width=60%>  
  
ひとまずダンパはモデル化の対象外（ダクト抵抗で模擬する）とし、ファン構成とエアバランスを考える。  
[FlowBalance_1Room_SAFan_RAFan_EAFan.py](https://github.com/ShoheiMiyata/phyvac/blob/main/MainSample/%E7%A9%BA%E8%AA%BF%E6%A9%9F%E3%81%AE%E3%83%95%E3%82%A1%E3%83%B3%E6%A7%8B%E6%88%90%E3%81%A8%E3%82%A8%E3%82%A2%E3%83%90%E3%83%A9%E3%83%B3%E3%82%B9%E3%81%AB%E9%96%A2%E3%81%99%E3%82%8B%E8%80%83%E5%AF%9F/FlowBalance_1Room_SAFan_RAFan_EAFan.py) は1室にSA・RA・EAファンが接続された場合  
[FlowBalance_1Room_SAFan_RAFan_EAFan_Infiltration.py](https://github.com/ShoheiMiyata/phyvac/blob/main/MainSample/%E7%A9%BA%E8%AA%BF%E6%A9%9F%E3%81%AE%E3%83%95%E3%82%A1%E3%83%B3%E6%A7%8B%E6%88%90%E3%81%A8%E3%82%A8%E3%82%A2%E3%83%90%E3%83%A9%E3%83%B3%E3%82%B9%E3%81%AB%E9%96%A2%E3%81%99%E3%82%8B%E8%80%83%E5%AF%9F/FlowBalance_1Room_SAFan_RAFan_EAFan_Infiltration.py) はすき間（上図ij）のある1室にSA・RA・EAファンが接続された場合  
の流量バランス計算を表し、  
[FlowBalance_1Room_SAFan_RAFan_EAFan_Infiltration_PIDbalaning.py](https://github.com/ShoheiMiyata/phyvac/blob/main/MainSample/%E7%A9%BA%E8%AA%BF%E6%A9%9F%E3%81%AE%E3%83%95%E3%82%A1%E3%83%B3%E6%A7%8B%E6%88%90%E3%81%A8%E3%82%A8%E3%82%A2%E3%83%90%E3%83%A9%E3%83%B3%E3%82%B9%E3%81%AB%E9%96%A2%E3%81%99%E3%82%8B%E8%80%83%E5%AF%9F/FlowBalance_1Room_SAFan_RAFan_EAFan_Infiltration_PIDbalancing.py)はファンinvやダクト抵抗をPID制御によって仮想的に調整するプログラムである。流量はファンによる加圧（invに応じてP-Q曲線は変形する）と、ダクトによる圧力損失（風量の2乗に比例）とが釣り合う点が本プログラムでは算出される。  
    
すき間あり、各ファンのP-Q曲線が以下で同一、ダクト抵抗係数は全て0.5 Pa/(m<sup>3</sup>/min)<sup>2</sup>とした場合、  
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
  
SAファン、ダクトab,cd,ce,ebを調整すると、`Fan_SA.inv=0.89, ab抵抗=2.01, cd抵抗=99.1, ce抵抗=0.104,eb抵抗=0.197`の時に以下のようになる。
```
室内外差圧:  0.001 Pa
各ダクトの風量(m3/min, 矢印の向きが正)
←f AEAファン: 2.0 －e－－－－ 9.0 ←－－－－－
                   ↓                        ｜
                  7.0     　　　   　  　 　 室 →d EAファン: 1.0
                   ｜                        c  →g すき間: 0.0
                   ｜                      　↑
→a －－－ 3.0 －－－b－－－→SAファン: 10.0 －－
```  
この状態Aから、
- 外気導入量：設計風量を維持（3.0を維持）
- 第3種換気排気量：設計風量固定（1.0を維持）  
  
しつつ、給気ファンを居室の温調VAV群の要求風量でインバータ制御する。この際、同じくSAファン、ダクトab,cd,ce,ebを調整する

`Fan_SA.inv=0.77, Fan_RA.inv=0.77 Fan_EA.inv=0.078, ab抵抗係数:1.66, ef抵抗係数:2.38`
```
室内外差圧:  0.002 Pa
各ダクトの風量(m3/min, 矢印の向きが正)
←f AEAファン: 2.0 －e－－－－ 5.0 ←－－－－－
                  ↓                     ｜
                 3.0     　　　   　  　 　 室 →d EAファン: 1.0
                  ｜                     c  →g すき間: -0.0
                  ｜                    　↑
→a－－－ 3.0 －－b－－－－→SAファン: 6.0 －－
```
> SAファンの圧力低下により、EA+RAファンの引っ張りが相対的に大きくなり、流入するすきま風が生じる。  
  
`Fan_SA.inv=0.61, Fan_RA.inv=0.77 Fan_EA.inv=0.078, ab抵抗係数:1.66, ef抵抗係数:2.38`
```
室内外差圧:  -0.497 Pa
各ダクトの風量(m3/min, 矢印の向きが正)
← 2.39 －－－RAファン: 8.57 ←－－
          ↓                  　 ｜
         6.18     　　　   　　  室 →EAファン: 0.42
          ｜                   　  →すき間: -1.0
          ｜                  　↑
→ 1.82 －－－→SAファン: 7.99 －－
```
> RAファンの引っ張りが強く、EAファンの風量が0に近づく。このままSAファンの回転数を落とすとEAファンの風量が0になる（計算上ファンは逆流しないものとしている）。
> `OA・RA・EAダンパ開度が同じなら、RA・OAはあるところまで同じ割合で減る`ことも確認された。SAファン風量減：RAファン風量減、SAファン風量減：OA風量減は一定である。
  
1.2 状態Aから、SAファンinvとEAファンinvのみ変化させる  
`Fan_SA.inv=0.77, Fan_RA.inv=0.77 Fan_EA.inv=0.095, ab抵抗係数:1.66, ef抵抗係数:2.38`
```
室内外差圧:  -0.302 Pa
各ダクトの風量(m3/min, 矢印の向きが正)
← 2.21 －－－RAファン: 8.78 ←－－
          ↓                  　 ｜
         6.56     　　　   　　  室 →EAファン: 1.0
          ｜                    　 →すき間: -0.78
          ｜                  　↑
→ 2.43 －－－→SAファン: 9.0 －－
```
> 1.1に対して、EAファンの風量増加分はそのまますき間風になっている。  
`Fan_SA.inv=0.66, Fan_RA.inv=0.77 Fan_EA.inv=0.13, ab抵抗係数:1.66, ef抵抗係数:2.38`
```
室内外差圧:  -1.168 Pa
各ダクトの風量(m3/min, 矢印の向きが正)
← 2.37 －－－RAファン: 8.53 ←－－
          ↓                     ｜
         6.16     　　　   　　  室 →EAファン: 1.0
          ｜                       →すき間: -1.53
          ｜                  　↑
→ 1.84 －－－→SAファン: 8.0 －－
```
> 1.1に対して、EAファンの風量増加分はそのまますき間風になっている。 
2. OA系ダクト抵抗係数も制御
0.723304223001003 0.7669184840517083 0.08535480100494616 0.3538671146246987 2.3815015460084754
```
室内外差圧:  -0.12 Pa
各ダクトの風量(m3/min, 矢印の向きが正)
← 2.49 －－－RAファン: 8.49 ←－－
          ↓                   ｜
         6.0     　　　   　　  　 室 →EAファン: 1.0
          ｜                     →すき間: -0.49
          ｜                  　↑
→ 3.0 －－－→SAファン: 9.0 －－
```
