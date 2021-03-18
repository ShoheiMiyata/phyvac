## Main code structure
The main code is structured as follows:
- read input files
- define equipment, branch and control
- time step calculation
  - input boundary condition such as outdoor air temperature, heat load, etc.
  - control equiment
  - flow balance calculation
  - temperature and power calculation
- save output files
## Code example - 1AHU_1simpleAHU.py
import modules used in this program
~~~
import phyvac as pv
import pandas as pd
import time
import copy
import numpy as np
import datetime
~~~
read input files
~~~
input_data = pd.read_csv("Input15min.csv", index_col=0, parse_dates=True)
input_data = input_data.resample('1min').interpolate()
~~~
create output dataframe
~~~
output_data = input_data.drop(input_data.columns[[0, 1, 2, 3, 4]], axis=1)
output_data = output_data.assign(g_load=0.0, AHU_g=0.0, AHU_tin=0.0, AHU_tout=0.0, AHU_vlv=0.0, dp_header=0.0, CP1_g=0.0, CP1_inv=0.0, CP1_pw=0.0,
                                 CP1_dp=0.0, CP1_ef=0.0, AHP1_g_ch=0.0, AHP1_tin_ch=0.0, AHP1_tout_ch=0.0, AHP1_COP=0.0,
                                 AHP1_pw=0.0, AHP1_pl=0.0, tdb=0.0)
~~~

## Main文の構成
main文は  
- 入力ファイルの読み込み
- 機器・枝・制御の定義
- 毎時刻計算
  - 外気温湿度や熱負荷などの境界条件の入力
  - 機器制御
  - 流量計算
  - 温度・消費電力計算
- 出力ファイルの保存  

という流れで構成されます。
