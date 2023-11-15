## pv.Window(wall_data, project_data, material_data, weather_data)
室温計算のための窓クラス。各種物理情報と計算対象期間における相当外気温度の情報を保有する。  
  
<img src="https://github.com/ShoheiMiyata/phyvac/assets/27459538/1479c01f-ec8e-4aa3-9aa6-5b0c16b97383.png" width=70%>  

  
window_dataから読み込まれる窓情報(例)  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|window_data|pandas.core.series.Series|1つの壁の情報|
|project_data|dict|プロジェクト情報|
|weather_data|pandas.core.frame.DataFrame|気象データ|
  
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
# 窓インスタンスのリストの作成(main文ではこの書き方)
windows = [pv.Window(windows_df.loc[i], project_df, weather_df) for i in list(windows_df.index)]
print(windows[0].window_id)
```
> 1

