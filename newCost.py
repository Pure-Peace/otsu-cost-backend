'''
@name: FUCKING-PP+-NOT-OPEN-SOURCE
@author: Pure-Peace
@version: 0.1
@date: 2020-07-20 00:13:21
'''

import requests
import re
from bs4 import BeautifulSoup
import time
import datetime
from ctypes import cdll, c_double


# load cost calculator from dll
calculator = cdll.LoadLibrary(r'./cost.so').costCalculate
calculator.restype = c_double


# get the cost (use pp+ data)
def handleCostCalculate(
        AimTotal=0,
        AimJump=0,
        AimFlow=0,
        Precision=0,
        Speed=0,
        Stamina=0,
        Accuracy=0,
        Sum=0,
        Average=0,
        Total=0,
        version=0
) -> float:
    if version == 1:
        # the old cost
        return (AimJump / 3000) ** 0.8 * (AimFlow / 1500) ** 0.5 + (Speed / 2000) ** 0.8 * (Stamina / 2000) ** 0.5 + (Accuracy / 2700)

    # new cost
    return calculator(AimJump, AimFlow, Speed, Accuracy, Stamina, Precision)


# get the pp+ Top Performances table data
def getTableData(soup: BeautifulSoup) -> dict:
    def fixScripts(scripts):
        return fixString(scripts[-1].text.strip(), ('\n', '\r', '\t'))

    scripts = fixScripts(soup.find_all(
        'script', attrs={'type': 'text/javascript', 'src': None}))
    tableData = eval(re.findall(r'table_data = (.*);var', scripts, re.I)[0])
    return tableData


# logger
def logg(text: str, *args) -> None:
    print('[{}] {}'.format(getTime(1), text), *args)


# get now time
def getTime(needFormat: int = 0, formatMS: bool = True) -> [int, str]:
    if needFormat != 0:
        return datetime.datetime.now().strftime(f'%Y-%m-%d %H:%M:%S{r".%f" if formatMS else ""}')
    return int(str(time.time()).split('.')[0])


# delete some word
def fixString(string: str, fix: [list, tuple] = (':', ',', 'pp', '(', ')', ' ')) -> str:
    for i in fix:
        string = string.replace(i, '')
    return string


# get digits from string
def getNumber(string: str) -> str:
    return ''.join(re.findall(r'\d+', string))


# get the player data from pp+ soup
def getPlayerData(soup: BeautifulSoup) -> dict:
    playerPanel = soup.find(
        'div', attrs={'class': 'panel-body player-panel'})
    playerInfo = playerPanel.find_all('a')

    playerName = playerInfo[0].text
    playerId = playerInfo[0].attrs.get('href').split('/')[-1]

    rank = int(getNumber(playerInfo[1].text))
    countryRank = getNumber(playerInfo[2].text)

    country = playerInfo[2].find_next('img').attrs.get('title')
    playcount = int(playerPanel.find('table').find_all('td')[1].text)

    return {'username': playerName, 'userid': playerId, 'rank': rank, 'country_rank': countryRank, 'country': country, 'playcount': playcount}


def getPlayerPerformance(soup: BeautifulSoup) -> dict:
    pp = soup.find('div', attrs={'class': 'performance-table'})
    ths = pp.find('tr', attrs={'class': 'perform-total'}).find_all('th')

    totalPerformance = int(fixString(ths[1].text))
    body = [fixString(i.text) for i in pp.find('tbody').find_all('td')]

    rawData = {body[i]: int(body[i+1]) for i in range(0, len(body), 2)}
    rawData['Total'] = totalPerformance
    return rawData


def header():
    return {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36 SE 2.X MetaSr 1.0'}


# get pp+ data from syrin.me (userKey = username || userid)
def getPlayerPlusData(userKey: [str, int]) -> [dict, bool]:

    logg(f' [{userKey}] is requesting pp+ data...')
    rawData = {}
    start = time.time()

    try:
        resp = requests.get(
            f'https://syrin.me/pp+/u/{userKey}/',
            timeout=60,
            headers=header()
        )

        logg(f' [{userKey}] get the html data! begin to parse...')
        soup = BeautifulSoup(resp.content, features='html5lib')

        logg(f' [{userKey}] parsing pp...')
        rawData['pp'] = getPlayerPerformance(soup)

        logg(f' [{userKey}] parsing player data...')
        rawData['player'] = getPlayerData(soup)

        logg(f' [{userKey}] parsing table data...')
        rawData['table'] = getTableData(soup)

        timeSpent = time.time() - start
        status = True
        logg(f' [{userKey}] parse done！get the pp+ data! time spent: {timeSpent}s')

    except Exception as err:

        logg(f' [{userKey}] get the pp+ data failed, error:', err)

        if rawData.get('pp'):
            status = True
        else:
            rawData, status = f' [{userKey}] get pp+ data failed', False

    return rawData, status


# try it here
if __name__ == '__main__':

    # get data
    rawData, status = getPlayerPlusData('5084172')

    # calculate the pp
    cost = handleCostCalculate(**rawData.get('pp'))

    # update
    rawData['cost'] = cost
