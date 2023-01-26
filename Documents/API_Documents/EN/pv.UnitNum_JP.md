## pv.UnitNum(thre_up=[0.5,1.0], thre_down=[0.4,0.9], t_wait=15, num=1)
Number control (controls the number of pumps and chillers based on the flow rate g. However, g does not necessarily have to be the flow rate. However, g does not necessary) 
<img src="https://user-images.githubusercontent.com/27459538/112745838-43f03d80-8fe6-11eb-8d2b-7ba1e58a3cae.png" width=40%>
  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|thre_up|list|Incremental thresholds (1->2 units, 2->3 units, etc.) thre: threshold|
|thre_down|list|Reduction threshold (2->1, 3->2, etc.) thre: threshold|
|t_wait|integer|Wating time (increase/decrease steps when the threshold value of increase/decrease steps is exceeded/reached for t_wait time consecutively)|
|num|integer|Number of units in operation|
|g|float|Flow rate (reference value when controlling the number of units)|
  
## pv.UnitNum.control(g)
Control the number of units based on g
  
### returns:
The number of units
  
## Sample codes
Target system：System with 2 pumps; initial 1 unit; increasing steps
<img src="https://user-images.githubusercontent.com/27459538/112746375-55871480-8fe9-11eb-8b22-dee30ced54fb.png" width=40%>

  
```
import phyvac as pv 
import matplotlib.pyplot as plt
import numpy as np

result = np.zeros((60,3))
CP1 = pv.Pump() # Definition of CP1 (default values are used for characteristics)
UnitNum_CP1 = pv.UnitNum(thre_up=[0.3], thre_down=[0.2], t_wait=15) # Definition of CP1's number of units control

for calstep in range(60):
    branch_g = calstep*0.01 # Assume flow rate increases by 0.01 per hour
    CP1.num = UnitNum_CP1.control(g=branch_g) # Execution of the number of units control
    result[calstep,0] = calstep
    result[calstep,1] = CP1.num
    result[calstep,2] = branch_g
    

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(result[:,0], result[:,1], c="r", label="num")
ax.plot(result[:,0], result[:,2], c="b", label="flow")
ax.grid(axis='both')
ax.legend() 
ax.set_xlabel('calstep') 
ax.set_ylabel("num,flow") 
```
> Result
> <img src="https://user-images.githubusercontent.com/27459538/112747216-cda40900-8fee-11eb-839b-52a34299483a.png" width=40%>
  
Target system: 3 pumps, 3 initial values, sample of reduced stages  
<img src="https://user-images.githubusercontent.com/27459538/112747245-00e69800-8fef-11eb-86c7-ad7a30870d61.png" width=40%>
  
```
import phyvac as pv
import matplotlib.pyplot as plt
import numpy as np

result = np.zeros((60,3))
CP1 = pv.Pump() 
CP1.num = 3
UnitNum_CP1 = pv.UnitNum(thre_up=[1.2,2.2], thre_down=[1.0,2.0], t_wait=15,num=3) # Definition of CP1 unit number control
UnitNum_CP1.num = 3

for calstep in range(60):
    branch_g = 3.0-calstep*0.05 # Assume flow rate decreases 0.05 per hour from 3.0
    CP1.num = UnitNum_CP1.control(g=branch_g) # Execution of the number of units control
    result[calstep,0] = calstep
    result[calstep,1] = CP1.num
    result[calstep,2] = branch_g
    

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(result[:,0], result[:,1], c="r", label="num")
ax.plot(result[:,0], result[:,2], c="b", label="flow")
ax.grid(axis='both')
ax.legend() 
ax.set_xlabel('calstep') 
ax.set_ylabel("num,flow") 
```
> Result
> <img src="https://user-images.githubusercontent.com/27459538/112747511-fa592000-8ff0-11eb-8a52-e67736ed8867.png" width=40%>
