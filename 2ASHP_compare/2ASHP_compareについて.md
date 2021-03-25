## 2ASHP_compareについて

### 1ASHP_simpleAHU.pyのシステム構成のうち、ASHPを2台に変更した場合の結果を比較します
結果は[Upload](https://github.com/ShoheiMiyata/phyvac/tree/main/2ASHP_compare/Upload)へアップロードしてください。  
<img src="https://user-images.githubusercontent.com/27459538/112437496-5cfcb280-8d8a-11eb-8b7a-826fe1b40f2b.png" width=60%>  
  
### 条件変更：
負荷流量・負荷熱量・流量が1ASHP_simpleAHU.pyの2倍になっています。

### 制御変更：  
ASHPの台数制御を追加してください  
効果待ち時間の例：  
ASHP1台運転時、負荷流量が0.12を上回ってから30分後に2台へ増段する  

<img src="https://user-images.githubusercontent.com/27459538/112437753-9df4c700-8d8a-11eb-8a7b-b3432c4689c5.png" width=60%>  
  
### その他：
基本的にはそのまま。  
ただし、うまく計算が回らない可能性があるため、PIパラメータを調整する必要があるかもしれません。
