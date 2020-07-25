from flask_sqlalchemy import SQLAlchemy

# mysql
db = SQLAlchemy()

# mysql config(s)
dbServer = 'your mysql address'
dbCharset = 'utf8'
dbPort = '3306'
dbName = 'database name'
dbUser = 'database user name'
dbPassword = 'password'


# import this
def connect():
    return f'mysql+pymysql://{dbUser}:{dbPassword}@{dbServer}:{dbPort}/{dbName}?charset={dbCharset}'


class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    userid = db.Column(db.String(100), primary_key=True)
    username = db.Column(db.String(100))
    cost = db.Column(db.Float)
    old_cost = db.Column(db.Float)
    player = db.Column(db.JSON)
    pp = db.Column(db.JSON)
    time = db.Column(db.DateTime)

    @property
    def getRawData(self):
        temp = {i.name: getattr(self, i.name) for i in self.__table__.columns if i.name not in (
            'username', 'userid'
        )}
        return temp
    
    @property
    def getAllData(self):
        temp = {i.name: getattr(self, i.name) for i in self.__table__.columns if i.name not in (
            'username', 'userid'
        )}
        tableObj = Table.query.get(self.userid)
        if tableObj:
            temp['table'] = tableObj.table
        return temp


class Record(db.Model):
    __tablename__ = 'records'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    userid = db.Column(db.String(100))
    username = db.Column(db.String(100))
    cost = db.Column(db.Float)
    old_cost = db.Column(db.Float)
    player = db.Column(db.JSON)
    pp = db.Column(db.JSON)
    time = db.Column(db.DateTime)
    
    @property
    def getDict(self):
        temp = {i.name: getattr(self, i.name) for i in self.__table__.columns if i.name not in (
            'username', 'userid'
        )}
        return temp


class Table(db.Model):
    __tablename__ = 'tables'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    userid = db.Column(db.String(100), primary_key=True)
    table = db.Column(db.JSON)
    time = db.Column(db.DateTime)
