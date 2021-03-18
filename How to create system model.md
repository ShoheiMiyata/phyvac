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
## Code example
'''
import pandas as pd
import time
import phyvac as pv
from tqdm import tqdm
import copy
import numpy as np
import datetime
'''

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
