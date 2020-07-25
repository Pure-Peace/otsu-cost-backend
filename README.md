# otsu-cost-backend
backend = api + spider + costCalculator

Website: https://cost.otsu.fun

Api: https://cost.otsu.fun/api

Built: Python3 + flask + flask-SQLAlchemy

Based on pp+ (https://syrin.me/)

# Run

1.Clone

```bash
git clone https://github.com/Pure-Peace/otsu-cost-backend
```

2.Dependencies

```bash
pip install -r requirements.txt
```

3.Run api


gunicorn (daemon)

```bash
gunicorn -c config.py engine:app
```

Run directly

```bash
python main.py
```

4.Spider

```bash
python spider.py
```


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
