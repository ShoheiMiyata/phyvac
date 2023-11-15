## pv.Room(room_data, project_data, schedule_data, walls, windows)
室温計算のための室クラス。自然室温やCO2濃度を計算する関数（cal）を有する。  
  
<img src="https://github.com/ShoheiMiyata/phyvac/assets/27459538/cd28e858-1380-4bba-8767-1f6fb072c696.png" width=90%>  

  
room_dataから読み込まれる室情報(例)  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|room_data|pandas.core.series.Series|1つの壁の情報|
|project_data|dict|プロジェクト情報|
|schedule_data|pandas.core.frame.DataFrame|気象データ|
  
## サンプルコード
```
import datetime
import test_phyvac as pv


start = datetime.datetime(year=2000, month=7, day=20, hour=00, minute=00, second=00)  # この日付から助走が始まる
end = datetime.datetime(year=2000, month=7, day=28, hour=0, minute=0, second=00)  # この日付の0:00になった瞬間、計算が終了

cal_dt = 60  # 計算時間間隔[s]

# 計算条件の読み込み
[project_df, rooms_df, walls_df, windows_df, schedule_df, material_df] = pv.read_conditions('Input/Rooms.xlsx', start, end, cal_dt)

# 気象データの読み込み・変換
weather_df = pv.convert_weatherdata('Input/WeatherData.xlsx', project_df, start, end)

# 窓インスタンスの作成
Window1 = pv.Window(windows_df.loc[1], project_df, weather_df)
print(Window1.window_id, Window1.window_area)
```
> 1 21.6
```
# 窓リストの作成(main文ではこの書き方)
windows = [pv.Window(windows_df.loc[i], project_df, weather_df) for i in list(windows_df.index)]
print(windows[0].window_id)
```
> 1

