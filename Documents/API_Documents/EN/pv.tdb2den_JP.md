## tdb2den(tdb)
Function to calculate density [kg/m<sup>3</sup>] from dry bulb temperature [&deg;C]    
### Parameters:
|  name  |  type  | description |
| ---- | ---- | ---- |
|tdb|float|Dry Bulb Temperature[&deg;C]|
  
### returns:
Density[kg/m<sup>3</sup>]
  
## Sample codes  
```
import phyvac as pv

print(pv.tdb2den(30.0))
print(pv.tdb2den(20.0))
print(pv.tdb2den(10.0))
```
> Results  
> 1.1654910949868074  
> 1.2052418144611186  
> 1.2477997881355931  
