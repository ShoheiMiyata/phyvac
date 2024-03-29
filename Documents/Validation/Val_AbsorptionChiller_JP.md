## 吸収式冷温水機　単体機器クラスの検証
### テストケースと計算結果  
|Case No.|入力| | | |制御目標値|計算結果| | | |
|:----|:----|:----|:----|:----|:----|:----|:----|:----|:----|
| |冷水入口温度 [℃]|冷水流量 [%]|冷却水入口温度 [℃]|冷却水流量 [%]|冷水出口温度 [℃]|冷却水出口温度 [℃]|能力 [kW]|ガス消費量 [m3/h]|消費電力 [kW]|
|E-AR100|12|100|32|100|7| |527|32.39486|5.1|
|E-AR101|10.75|100|27|100|7| |396.0414|23.67874|5.1|
|E-AR102|9.5|100|22|100|7| |264.0276|14.79049|5.1|
|E-AR110|12|75|27|75|7| |396.0414|23.67874|5.1|
|E-AR111|10|86|32|86|5| |454.1275|29.89833|5.1|
|E-AR120|14|100|32|100|9| |527|31.56803|5.1|

※冷却水出口温度は出力されていない



### 他ツールとの比較  
<img src="https://user-images.githubusercontent.com/27459538/213089533-83298e40-fc38-4df4-9095-a322ab6b522b.png" width=70%>  
<img src="https://user-images.githubusercontent.com/27459538/213089626-2686a82c-1ee1-46ab-9550-50c01ee42ca2.png" width=70%>  
<img src="https://user-images.githubusercontent.com/27459538/213089666-e5dafae7-96ce-480d-aa89-60c008704df8.png" width=70%>  

- 概ねメーカ提供値と同じ傾向
- 本モデルは消費電力が運転条件によって変化するモデルではない
