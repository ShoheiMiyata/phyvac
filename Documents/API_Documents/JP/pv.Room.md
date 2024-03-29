## pv.Room(room_data, project_data, schedule_data, walls, windows)
室温計算のための室クラス。自然室温やCO2濃度を計算する関数（cal）を有する。  
  
<img src="https://github.com/ShoheiMiyata/phyvac/assets/27459538/cd28e858-1380-4bba-8767-1f6fb072c696.png" width=90%>  

  
room_dataから読み込まれる室情報(例)  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|room_data|pandas.core.series.Series|1つの室の情報|
|project_data|dict|プロジェクト情報|
|schedule_data|pandas.core.frame.DataFrame|各種スケジュールデータ|
|walls|list|壁インスタンスのリスト|
|windows|list|窓インスタンスのリスト|
|rooms|list|室インスタンスのリスト|
|step|int|計算ステップ|
|rooms|list|室インスタンスのリスト|
|g_sa|float|給気風量 /[m3/min]|
|t_sa|float|給気温度 /['C]|
|w_sa|float|給気絶対湿度 /[kg/kg]|
|cp2_sa|float|給気CO2濃度 /[ppm]|
|g_infiltration|float|隙間風風量 /[m3/min] (流入:+, 流出: -)|
|t_outdoor|float|外気温度 /['C]|
|w_outdoor|float|外気絶対湿度 /[kg/kg]|

## pv.Room.cal(rooms, step, g_sa, t_sa, w_sa, co2_sa, g_infiltration, t_outdoor, w_outdoor)
給気と隙間風から室温を算出する
  
### returns:
なし（各インスタンスに更新された値が格納される）
  
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
# 壁・窓インスタンスのリストの作成
walls = [pv.Wall(walls_df.loc[i], project_df, material_df, weather_df) for i in list(walls_df.index)]
windows = [pv.Window(windows_df.loc[i], project_df, weather_df) for i in list(windows_df.index)]

# 室インスタンスの作成
Room2 = pv.Room(rooms_df.loc[2], project_df, schedule_df, walls, windows)
print(Room2.room_id, Room2.volume)


```
> 2 566.4000000000001
```
# 室インスタンスのリストの作成
rooms = [pv.Room(rooms_df.loc[i], project_df, schedule_df, walls, windows) for i in list(rooms_df.index)]
print(rooms[1].room_id, rooms[1].volume, rooms[1].t_room, rooms[1].w_room)
```
> 2 566.4000000000001 26 0.010496860875
```
# 非空調時（給気風量=0.0）の計算
for cal_step in range(int((end - start).total_seconds() / cal_dt + 1)):
    for Room in rooms:
        Room.cal(rooms=rooms, step=cal_step, g_sa=0.0, t_sa=14.0, w_sa=0.005, co2_sa=600.0, g_infiltration=10.0, t_outdoor=weather_df['Temperature'].iat[cal_step], w_outdoor=weather_df['Humidity'].iat[cal_step])

print(rooms[1].t_room, rooms[1].w_room)
```
> 33.32135674803487 0.0313833700943817
