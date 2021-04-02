### 空調機のファン構成とエアバランスに関するケーススタディ
  
<img src="https://user-images.githubusercontent.com/27459538/113409126-99b05580-93eb-11eb-8ad0-6fbdaebfe9fc.png" width=60%>  
  
ひとまずダンパはモデル化の対象外（ダクトの圧力損失で模擬する）とし、ファン構成とエアバランスを考える。  
[FlowBalance_1Room_SAFan_RAFan_EAFan.py](https://github.com/ShoheiMiyata/phyvac/blob/main/MainSample/%E7%A9%BA%E8%AA%BF%E6%A9%9F%E3%81%AE%E3%83%95%E3%82%A1%E3%83%B3%E6%A7%8B%E6%88%90%E3%81%A8%E3%82%A8%E3%82%A2%E3%83%90%E3%83%A9%E3%83%B3%E3%82%B9%E3%81%AB%E9%96%A2%E3%81%99%E3%82%8B%E8%80%83%E5%AF%9F/FlowBalance_1Room_SAFan_RAFan_EAFan.py) は1室にSA・RA・EAファンが接続された場合  
[FlowBalance_1Room_SAFan_RAFan_EAFan_Infiltration.py](https://github.com/ShoheiMiyata/phyvac/blob/main/MainSample/%E7%A9%BA%E8%AA%BF%E6%A9%9F%E3%81%AE%E3%83%95%E3%82%A1%E3%83%B3%E6%A7%8B%E6%88%90%E3%81%A8%E3%82%A8%E3%82%A2%E3%83%90%E3%83%A9%E3%83%B3%E3%82%B9%E3%81%AB%E9%96%A2%E3%81%99%E3%82%8B%E8%80%83%E5%AF%9F/FlowBalance_1Room_SAFan_RAFan_EAFan_Infiltration.py) はすき間（上図ij）のある1室にSA・RA・EAファンが接続された場合  
の流量バランス計算を表す。
  
すき間あり、各ファンのP-Q曲線が以下で同一、圧力損失係数は全て0.5 Pa/(m3/min)^2とした場合、  
<img src="https://user-images.githubusercontent.com/27459538/113414238-860aec00-93f7-11eb-8d3e-32d4adf9698a.png" width=40%>  

`Fan_SA.inv = 1.0, Fan_RA.inv = 1.0, Fan_EA.inv = 1.0`で（inv=1.0で100%(50Hz or 60Hz)）
```
室圧:  -29.48 Pa
各ダクトの風量(m3/min, 矢印の向きが正)
← 3.24 －－－ 10.35 :RAファン←－－
          ↓                      ｜
         7.1     　　　   　　 　 室 →EAファン: 10.76
          ｜                        →すき間: -7.68
          ｜                  　 ↑
→ 6.32 －－－→SAファン: 13.43 －－
```
となる。EAファンの引っ張りが強く、室圧が負圧に、流入すきま風が大きい。  
エアバランスを下図のように調整することも可能。  
<img src="https://user-images.githubusercontent.com/27459538/113411222-2fe67a80-93f0-11eb-928d-2066b77694a2.png" width=40%>  
  
その場合、各種ファンのみを調整すると、`Fan_SA.inv = 0.84, Fan_RA.inv = 0.74, Fan_EA.inv = 0.08`の時に以下のようになる。
```
室圧:  -0.0 Pa
各ダクトの風量(m3/min, 矢印の向きが正)
← 3.42 －－－ 9.01 :RAファン←－－
          ↓                      ｜
         5.58     　　　   　　   室 →EAファン: 1.01
          ｜                      →すき間: -0.01
          ｜                  　 ↑
→ 4.41 －－－→SAファン: 10.01 －－
```
さらに、外気導入と排気のダクトの圧力損失係数を調節すると以下のようになる。
```
室圧:  -0.0 Pa
各ダクトの風量(m3/min, 矢印の向きが正)
← 2.01 －－－ 9.01 :RAファン←－－
          ↓                    ｜
         7.0     　　　   　　  室 →EAファン: 1.0
          ｜                      →すき間: -0.01
          ｜                  　↑
→ 2.99 －－－→SAファン: 10.0 －－
```
このとき、`Fan_SA.inv = 0.90, Fan_RA.inv = 0.73, Fan_EA.inv = 0.08, abの圧力損失係数:2.30, efの圧力損失係数：0.96`であった。。  
なお、調整は各ファンのinvとab・efの圧力損失係数を仮想的にPI制御しておこなった。
