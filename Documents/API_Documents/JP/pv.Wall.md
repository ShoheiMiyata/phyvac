## pv.Wall(wall_data, project_data, material_data, weather_data)
室温計算のための壁クラス。各種物理情報と計算対象期間における相当外気温度の情報を保有する。  
  
<img src="https://github.com/ShoheiMiyata/phyvac/assets/27459538/a47590db-d2e6-4dcf-a9e1-889fde78c800.png" width=70%>  
  
wall_dataで読み込まれる壁情報(例)  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|wall_data|pandas.core.series.Series|1つの壁の情報|
|project_data|dict|プロジェクト情報|
|material_data|pandas.core.frame.DataFrame|材料情報|
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

# 壁インスタンスの作成(表のwall_idが1の壁）
Wall1 = pv.Wall(walls_df.loc[1], project_df, material_df, weather_df)
print(Wall1.wall_type, Wall1.wall_id)  # Wall1の部屋番号
```
> outer_wall 1
```
# 壁のインスタンスをまとめて作成し、リスト化 (main文ではこの記述方法)
walls = [pv.Wall(walls_df.loc[i], project_df, material_df, weather_df, cal_dt) for i in list(walls_df.index)]
print(walls[0].wall_id)
```
> 1

