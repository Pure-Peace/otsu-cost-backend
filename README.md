# otsu-cost-backend
backend = api + spider + costCalculator

Website: https://cost.otsu.fun
Api: https://cost.otsu.fun/api
Built: Python3 + flask + flask-SQLAlchemy


# Simple Document:

getPlayerList

```
https://cost.otsu.fun/api/player_list
https://cost.otsu.fun/api/player_list?country=US
```

playerlist pagination, count limit

```
https://cost.otsu.fun/api/player_list?count=100&page=1
https://cost.otsu.fun/api/player_list?country=CN&count=100&page=1
```

sort by pp or skills: pp_order

```
https://cost.otsu.fun/api/player_list?pp_order=PlaycountDown
https://cost.otsu.fun/api/player_list?pp_order=PlaycountDown&page=1&country=CN
```

all pp_orders here:
```
Total
AimTotal
AimJump
AimFlow
Speed
Stamina
Accuracy
Precision
Average
Sum
NewCost
OldCost
CostDiff
CostDiffDown
Playcount
PlaycountDown
```



player info (changed)

```
https://cost.otsu.fun/api/player_record/explosive
```

player info (just info)

```
https://cost.otsu.fun/api/player/explosive
```

player info (include best performance)

```
https://cost.otsu.fun/api/player/explosive?size=complete
```


refresh player info

```
https://cost.otsu.fun/api/player/explosive?method=force
```


player best performance list

```
https://cost.otsu.fun/api/player_bp
```

count limit and pagination

```
https://cost.otsu.fun/api/player_bp?count=4&page=1
```
