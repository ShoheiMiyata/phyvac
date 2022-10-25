# phyvac

python+hvac => phyvac [fívək | fái-]  

## Tutorial   チュートリアル  
[How to create a main code](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/Tutorials/How%20to%20create%20a%20main%20code.md) - [メイン文のつくり方](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/Tutorials/%E3%83%A1%E3%82%A4%E3%83%B3%E6%96%87%E3%81%AE%E3%81%A4%E3%81%8F%E3%82%8A%E6%96%B9.md)  
[流量バランス計算(水側)：AHU1台、Chiller3台](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/Tutorials/%E6%B5%81%E9%87%8F%E3%83%90%E3%83%A9%E3%83%B3%E3%82%B9%E8%A8%88%E7%AE%97(%E6%B0%B4%E5%81%B4)%EF%BC%9AAHU1%E5%8F%B0%E3%80%81Chiller3%E5%8F%B0.md)  
[流量バランス計算(水側)：AHU2台、Chiller2台、送水二次ポンプ](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/Tutorials/%E6%B5%81%E9%87%8F%E3%83%90%E3%83%A9%E3%83%B3%E3%82%B9%E8%A8%88%E7%AE%97(%E6%B0%B4%E5%81%B4)%EF%BC%9AAHU2%E5%8F%B0%E3%80%81Chiller2%E5%8F%B0%E3%80%81%E9%80%81%E6%B0%B4%E4%BA%8C%E6%AC%A1%E3%83%9D%E3%83%B3%E3%83%97.md)  
[流量バランス計算(空気側)：1室、OAファン、RAファン、EAファン]()  

## Question and Discussion 質問・議論
分からないことや気になることがありましたら下記リンクに投稿して議論しましょう  
https://groups.google.com/g/phyvac


## API Document   APIドキュメント
[List](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/API_Document_List.md) - [リスト](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/API_Documents/API%E3%83%89%E3%82%AD%E3%83%A5%E3%83%A1%E3%83%B3%E3%83%88%E3%83%AA%E3%82%B9%E3%83%88.md)  

## Validation 検証  
プログラムの計算の妥当性について検証をおこなっています。  
[List](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/Validation/Validation_List_JP.md) - [リスト](https://github.com/ShoheiMiyata/phyvac/blob/main/Documents/Validation/Validation_List_JP.md)  

## License
The phyvac is available under a 3-clause BSD-license.

## Update アップデート  
- 2022/08/31 Pumpモデルで定義時に性能曲線を図示するよう修正
- 2022/08/22 VRFモデル、GeoThermalHPモデル、吸収式冷凍機モデルの追加　その他微修正
- 2021/07/14 湿球温度計算の修正（大気圧の単位修正）、CoolingTowerの比エンタルピー単位修正
- 2021/06/28 Branch00系の廃止、Branch_wの追加（水系Branch）
- 2021/04/02 Branch100の追加（空気系Branch）

### [To Do リスト](https://github.com/ShoheiMiyata/phyvac/projects/1)


### python命名規則
https://qiita.com/naomi7325/items/4eb1d2a40277361e898b
  
### Markdown記法
https://www.markdown.jp/syntax/  
https://qiita.com/kamorits/items/6f342da395ad57468ae3  
http://danpansa.blog.jp/archives/21332987.html
