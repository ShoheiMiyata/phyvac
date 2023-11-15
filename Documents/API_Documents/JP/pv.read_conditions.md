## pv.read_conditions(filename, start, end, timedelta)
室温計算のための計算条件を読み込む関数。Rooms.xlsxの各シートの情報をpandas dataframeに格納する。  
スケジュール情報は指定した計算開始・終了時刻と計算時間間隔に基づき変換される。
![image](https://github.com/ShoheiMiyata/phyvac/assets/27459538/704b9aa7-9b7a-4769-a3bb-fa14776a8a17)

### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|filename|str|ファイルの場所・ファイル名|
|start|datetime.datetime|計算開始時刻|
|end|datetime.datetime|計算終了時刻|
|timedelta|int|計算時間間隔 (1~) \[s] |
  
### returns:
各シートの情報がpandas dataframeに格納されてリストとして返される。
[Projectシート, Roomsシート, Wallsシート, Scheduleシート, Materialシート]

  
## サンプルコード
```
import phyvac as pv # phyvacモジュールのインポート
import timedate

start = datetime.datetime(year=2000, month=7, day=20, hour=00, minute=00, second=00)  # 計算開始時刻の設定
end = datetime.datetime(year=2000, month=7, day=28, hour=0, minute=0, second=00)  # 計算終了時刻の設定

cal_dt = 60  # 計算時間間隔[s]

# 計算条件の読み込み
[project_df, rooms_df, walls_df, windows_df, schedule_df, material_df] = pv.read_conditions('Input/Rooms.xlsx', start, end, cal_dt) # Rooms.xlsxがphyvac.pyのフォルダに対してInput/Rooms.xlsxにある場合
print(material_df.iloc[0])
```
>heat conductivity[m2K/W]               1.4  
>volumetric specific heat[kJ/m3K]    1934.0  
>Name: concrete, dtype: float64  
```
print(schedule_df)
```
  0    1    2    3    4    5    6    7    8    9   10   11  
schedule_id  
2000-07-20 00:00:00  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  
2000-07-20 00:01:00  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  
2000-07-20 00:02:00  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  
2000-07-20 00:03:00  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  
2000-07-20 00:04:00  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  
...                  ...  ...  ...  ...  ...  ...  ...  ...  ...  ...  ...  ...  
2000-07-27 23:56:00  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  
2000-07-27 23:57:00  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  
2000-07-27 23:58:00  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  
2000-07-27 23:59:00  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  
2000-07-28 00:00:00  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  0.0  
