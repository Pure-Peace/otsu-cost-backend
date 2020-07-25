'''
主程序
@author: PurePeace
@time: 2020年2月10日 02:03:09
'''


import time, datetime, re, requests, random, json
from bs4 import BeautifulSoup

requests.adapters.DEFAULT_RETRIES = 999 # 增加重连次数


# get now timeString or timeStamp
def getTime(needFormat=0, formatMS=True):
    if needFormat != 0:
        return datetime.datetime.now().strftime(f'%Y-%m-%d %H:%M:%S{r".%f" if formatMS else ""}')
    else:
        return time.time()


# breakTime：每爬一页休息几秒
def getPage(country='CN', index=1, breakTime=1, datas=[], startTime=0):
    if datas != None and len(datas) > 0:
        #print(f'[{getTime(1)}]：已获取第{index}页数据共{len(datas)}条，耗时：{round(getTime()-startTime, 3)}s.\n')
        return datas

    time.sleep(breakTime + random.random())
    header = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'}
    #print(f'[{getTime(1)}]：正在获取第{index}页数据...')
    startTime = getTime()
    try:
        page = requests.get(f'https://osu.ppy.sh/rankings/osu/performance?country={country}&page={index}', headers=header, timeout=30)
        soup = BeautifulSoup(page.text, 'lxml')
        datas = soup.find_all('tr', attrs={'class':'ranking-page-table__row'})
    except:
        datas = []

    if len(datas) == 0 or datas == None:
        #print(f'[{getTime(1)}]：获取第{index}页数据时失败，稍后进行重试...')
        time.sleep(breakTime * 3 + random.random())

    return getPage(country, index, breakTime, datas, startTime)


def userData(pageData, index=0):
    needs = ('rank','acc','pc','pp','ss','s','a')
    number = re.compile(r'\d+\.?\d*')
    se = pageData[index].find_all('td', attrs={'class': 'ranking-page-table__column'})
    user = se.pop(1).find('a', attrs={'class': 'ranking-page-table__user-link-text js-usercard'})
    userid = user.attrs.get('data-user-id')
    username = user.text.strip()
    data = { k: number.findall(se[i].text.replace(',',''))[0] for i, k in enumerate(needs) }
    data['username'], data['userid'] = username, userid
    if 'ranking-page-table__row--inactive' in pageData[index].attrs['class']: data['status'] = 'inactive'
    else: data['status'] = 'active'
    return data


def fetchData(startPage=1, endPage=1, country='CN'):
    from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
    data = []
    print(f'[{getTime(1)}]：开始工作，抓取行政区：[{country}]；起始页：{startPage}，结束页：{endPage}\n')
    #for idx in range(startPage, endPage+1):
    #    thisPage = getPage(country, index=idx)
    #    userDatas = [userData(thisPage, index=i) for i in range(len(thisPage))]
    #    data.append({'country': country, 'page': idx, 'data': userDatas, 'time': getTime(1)})
    def getDone(f):
        thisPage = f.result()
        userDatas = [userData(thisPage, index=i) for i in range(len(thisPage))]
        data.append({'country': country, 'page': idx, 'data': userDatas, 'time': getTime(1)})
        print(f'\r当前任务已完成({len(data)}/{endPage-startPage+1})', end='')
    
    
    with ThreadPoolExecutor(max_workers=16) as executor:
        tasks = []
        for idx in range(startPage, endPage + 1):
            ft = executor.submit(getPage, country, index=idx)
            ft.add_done_callback(getDone)
            tasks.append(ft)
        wait(tasks, return_when=ALL_COMPLETED)
    
    return {'data': data, 'country': country, 'time': getTime(1)}


# country: 
# '' == global ranking;
# 'CN', 'US, 'UK' ... == country ranking
def getRankings(country=''):
    startPage=60
    endPage=100

    sstart = time.time()
    print(f'开始排行榜！起始：{startPage}，终止：{endPage}，地区：{country}')
    data = fetchData(startPage=startPage, endPage=endPage, country=country)
    print('完毕。')
    return data

if __name__ == '__main__':
    # go
    data = getRankings()

    # fix data
    print('开始处理玩家...')
    players = []
    for page in data['data']:
        for player in page['data']:
            players.append(player)
            #print(player['userid'])

    print('完毕，全部玩家：', len(players))


    # request local api to get player data, and calculate cost
    print('开工...')
    tries = 0
    for p in players:
        try:
            tries += 1
            print(f'[{tries}] do -> ',p['userid'])
            dstart = time.time()
            r = requests.get('http://127.0.0.1:8989/player/{}'.format(p['userid']), timeout=120)
            d = r.json()
            ddone = time.time() - dstart
            if d.get('status') == 0:
                print(f'[{tries}] sb(0) -> ', p['userid'], f' ({ddone})s')
                players.append(p)
            print(f'[{tries}] done -> ',p['userid'], f' ({ddone})s')
        except:
            ddone = time.time() - dstart
            print(f'[{tries}] sb(1) -> ', p['userid'], f' ({ddone})s')
            players.append(p)

            
    print('任务完成，总用时：', time.time() - sstart, 's')
