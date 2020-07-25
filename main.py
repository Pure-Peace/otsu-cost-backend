

from gevent import monkey; monkey.patch_all()
from gevent.pywsgi import WSGIServer

from flask import Flask, jsonify, request
from flask_cors import CORS
import database
import json
import newCost
#import redis
import requests

#rds = redis.Redis(host='localhost', port=6379, db=2)

logg = newCost.logg

# initial(s)
app = Flask(__name__)
app.config.update(RESTFUL_JSON=dict(ensure_ascii=False))
app.config["JSON_AS_ASCII"] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = database.connect()

database.db.init_app(app)
CORS(app)
with app.app_context():
    database.db.create_all()


def getCountryFilters(req):
    filters = set()
    country = req.get('country')
    if country and country != 'ALL':
        filters.add(database.User.player['country'] == country)
    return filters


def getPpOrders(req):
    orders = set()
    ppOrder = req.get('pp_order', 'Total')
    if ppOrder in ('Total', 'AimTotal', 'AimJump', 'AimFlow', 'Accuracy', 'Speed', 'Stamina', 'Precision', 'Average', 'Sum'):
        orders.add(database.User.pp[ppOrder].desc())
    else:
        if ppOrder == 'NewCost':
            orders.add(database.User.cost.desc())
        elif ppOrder == 'OldCost':
            orders.add(database.User.old_cost.desc())
        elif ppOrder == 'CostDiff':
            orders.add(database.User.cost - database.User.old_cost.desc())
        elif ppOrder == 'CostDiffDown':
            orders.add(database.User.cost - database.User.old_cost)
        elif ppOrder == 'Playcount':
            orders.add(database.User.player['playcount'].desc())
        elif ppOrder == 'PlaycountDown':
            orders.add(database.User.player['playcount'])
        else:
            orders.add(database.User.pp['Total'].desc())
    return orders


@app.route('/')
def root():
    return jsonify({'message': 'hello', 'status': 1})


@app.route('/player_list')
def playerList():
    pagination = None
    
    req = request.args
    filters = getCountryFilters(req)
    ppOrders = getPpOrders(req)
    
    if req.get('method') != 'unlimit':
        count, page = getPagination(req, 50, 1)
        pagination = database.User.query.order_by(*ppOrders).filter(*filters).paginate(page, count, False)
        data = pagination.items
    else:
        data = database.User.query.order_by(*ppOrders).filter(*filters).all()
    
    re = {'data': [(i.getAllData if req.get('size') == 'complete' else i.getRawData) for i in data], 'message': '成功获取', 'status': 1}
    if pagination:
        re['pages'] = {'total': pagination.pages, 'index': pagination.page, 'count': count}
    return jsonify(re)


@app.route('/player_bp')
def playerBp():
    pagination = None
    
    req = request.args
    filters = getCountryFilters(req)
        
    if req.get('method') != 'unlimit':
        count, page = getPagination(req, 5, 1)
        pagination = database.Table.query.filter(*filters).paginate(page, count, False)
        data = pagination.items
    else:
        data = database.Table.query.filter(*filters).all()
        
    re = {'data': [{'userid': i.userid, 'table': i.table, 'time': i.time} for i in data], 'message': '成功获取', 'status': 1}
    if pagination:
        re['pages'] = {'total': pagination.pages, 'index': pagination.page, 'count': count}
    return jsonify(re)


@app.route('/get_bp/<userid>')
def getBp(userid):
    pagination = None
    re = {'data': {}, 'message': '获取失败', 'status': -1}
    
    item = database.Table.query.get(userid)
    if item:
        re = {'data': {'table': item.table, 'time': item.time}, 'message': '成功获取', 'status': 1}
    return jsonify(re)


@app.route('/country_list')
def countryList():
    data = {}
    origin = database.User.query.with_entities(database.User.player['country']).all()
    for i in origin:
        if i[0]:
            key = i[0]
            if data.get(key, False): data[key] += 1
            else: data[key] = 1
    return jsonify({'data': data, 'message': '成功获取地区列表', 'status': 1})
    


@app.route('/player_record/<userid>')
def playerRecord(userid):
    userid = getUserid(userid)
    pagination = None
    
    req = request.args
    if req.get('method') != 'unlimit':
        count, page = getPagination(req, 10, 1)
        pagination = database.Record.query.filter_by(userid=userid).paginate(page, count, False)
        data = pagination.items
    else:
        data = database.Record.query.filter_by(userid=userid).all()
        
    re = {'data': [i.getDict for i in data], 'message': '成功获取', 'status': 1}
    if pagination:
        re['pages'] = {'total': pagination.pages, 'index': pagination.page, 'count': count}
    return jsonify(re)


def getPagination(req, count=10, page=1):
    countTemp = req.get('count', count)
    pageTemp = req.get('page', page)
    
    try: count = int(countTemp)
    except: pass
        
    try: page = int(pageTemp)
    except: pass
    
    return count, page



# fixer
def getUserid(userid):
    try:
        reqData = requests.get('http://112.74.52.149:9529/getPlayerDataV1?playerKey={}&action=simple'.format(userid), timeout=6).json()
        if reqData['status'] == 1: 
            userid = reqData['data']['osuid']
    except:
        pass
    return userid


@app.route('/player/<userid>')
def player(userid):
    userid = getUserid(userid)
    req = request.args
    if req.get('method') != 'force':
        user = database.User.query.get(userid)
        if user:
            rawData = (user.getAllData if req.get('size') == 'complete' else user.getRawData)
            return jsonify({'data': rawData, 'message': f'成功获取到{userid}的cost（历史）', 'status': 2})
        
    #if rds.get(userid) != None:

        
    rawData, status = newCost.getPlayerPlusData(userid)
    if status != True:
        return jsonify({'data': {}, 'message': f'暂时无法获取到{userid}的cost，请等待片刻', 'status': -1})
    
    
    cost = newCost.handleCostCalculate(**rawData.get('pp'))
    oldCost = newCost.handleCostCalculate(**rawData.get('pp'), version=1)
    rawData['cost'] = cost
    rawData['old_cost'] = oldCost
    rawData['time'] = newCost.getTime(1)
    
    saveToDatabase(rawData)
    if req.get('size') == 'simple': del(rawData['table'])
    return jsonify({'data': rawData, 'message': f'成功获取到{userid}的cost', 'status': 1})



def saveToDatabase(rawData):
    userid = rawData.get('player')['userid']
    logg(f' [{userid}] saving data to database...')
    
    # save to table users
    user = database.User.query.get(userid)
    if user == None:
        database.db.session.add(
            database.User(
                userid = userid,
                username = rawData.get('player')['username'],
                cost = rawData.get('cost'),
                old_cost = rawData.get('old_cost'),
                player = rawData.get('player'),
                pp = rawData.get('pp'),
                time = rawData.get('time')
            )
        )
    else:
        user.name = rawData.get('player')['username'],
        user.cost = rawData.get('cost'),
        user.player = rawData.get('player'),
        user.pp = rawData.get('pp'),
        user.time = rawData.get('time')
    
    # save to table tables
    table = database.Table.query.get(userid)
    if table == None:
        database.db.session.add(
            database.Table(
                userid = userid,
                table = rawData.get('table'),
                time = rawData.get('time')
            )
        )
    else:
        table.userid = userid
        table.table = rawData.get('table'),
        table.time = rawData.get('time')
        
    # add the record
    database.db.session.add(
        database.Record(
            userid = userid,
            username = rawData.get('player')['username'],
            cost = rawData.get('cost'),
            old_cost = rawData.get('old_cost'),
            player = rawData.get('player'),
            pp = rawData.get('pp'),
            time = rawData.get('time')
        )
    )
    
    database.db.session.commit()
    logg(f' [{userid}] complete!')
    #rds.set(key, value, ex=expireS)




if __name__ == '__main__':
    #WSGIServer(("0.0.0.0", 5000), app).serve_forever()
    app.run('127.0.0.1', 8989)