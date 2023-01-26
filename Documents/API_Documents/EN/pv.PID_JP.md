## pv.PID(mode=1, a_max=1, a_min=0, kp=0.8, ti=10, sig=0, t_reset=30, kg=1, t_step=1)
PI control (D component is omitted in this module)
  
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|mode|integer|Operation mode: 1 for operation, 0 for non-operation|
|a|float|Controled values of pump INV and valve opening, ect. Range(0~1)|
|a_max,a_min|float|Maximum and minimum values|
|kp|float|Proportional gain|
|ti|float|Integral term|
|sv|float|Set value|
|mv|float|Measured value (control target value) relative to setpoint. Flow rate, temperature, etc.|
|sig|float|Integral value of sv-mv|
|t_reset|float|Integral reset (set sig to 0 if positive and negative of sv-mv are always the same during t_reset)|
|kg|float|1 if the direction of increase/decrease of a and mv coinside, -1 if the opposite is true|
|t_step|integer|Control step. 1 for hourly control output, 2 for every 2 hours control output.|
  
## pv.PID.control(sv, mv)
Outputs PI control values based on setpoint sv and measured value mv
  
### returns:
Control value a
  
## Sample codes
System figure 
<img src="https://user-images.githubusercontent.com/27459538/112744451-1e116b80-8fdb-11eb-8a7b-259e715efa2c.png" width=40%>

  
```
import phyvac as pv
import matplotlib.pyplot as plt
import numpy as np

result = np.zeros((60,2))
CP1 = pv.Pump() # Definition of CP1 (default values are used for characteristics)
Branch = pv.Branch10(pump=CP1, kr_eq=1.3, kr_pipe=0.8) # Loop (branch) definition
PID_CP1 = pv.PID(kp=0.1, ti=30, a_min=0.0,t_reset=60) # Definition of PID control for CP1

for calstep in range(60):
    CP1_g_sv = 1.5 # Flow rate setting value is set at 1.5 m3/min
    CP1.inv = PID_CP1.control(sv=CP1_g_sv,mv=CP1.g) # Execution of PI control
    Branch.p2f(dp=0) # Single closed loop flow calculation with Branch inlet/outlet pressure difference = 0
    result[calstep,0] = calstep
    result[calstep,1] = CP1.g
    
plt.plot(result[:,0], result[:,1]) # Drawing Results
plt.xlabel("calstep") # x-axis labels
plt.ylabel("flow") # y-axis labels
plt.show()  
```
> Result (for kp=0.1, ti=30)  
> <img src="https://user-images.githubusercontent.com/27459538/112745087-bf4ef080-8fe0-11eb-93c3-b0092d55cb1f.png" width=40%>
  
> kp=0.02, ti=30 (the time required to reach the set value is longer because the proportional gain is smaller)    
> <img src="https://user-images.githubusercontent.com/27459538/112745137-371d1b00-8fe1-11eb-97cb-c3ce5f81ba8a.png" width=40%>
  
> kp = 0.02, ti = 3 (smaller integration time causes oscillation due to the greater influence of the deviation between the last measurement value and the set value)
> <img src="https://user-images.githubusercontent.com/27459538/112745258-0093d000-8fe2-11eb-90e9-2da8ccc8d93a.png" width=40%>
  
> kp=0.1, ti=30, t_step=3 (control is executed every 3 time steps)  
> <img src="https://user-images.githubusercontent.com/27459538/112745407-27063b00-8fe3-11eb-98bd-527d565f8ca8.png" width=40%>
