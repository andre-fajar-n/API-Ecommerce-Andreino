import pytest, json, logging, hashlib, uuid
from flask import Flask, request, json
from wsgi import cache
from blueprints import db, app 

from blueprints.book.model import Books
from blueprints.client.model import Clients
from blueprints.rent.model import Rent
from blueprints.models.users import UserModel

def call_client(request):
    client = app.test_client()
    return client

@pytest.fixture
def client(request):
    return call_client(request)

@pytest.fixture
def init_database():
    # create the database and the database table
    db.drop_all()
    db.create_all()
    
    salt = uuid.uuid4().hex
    encoded = ('%s%s' % ("password", salt)).encode('utf-8')
    hash_pass = hashlib.sha512(encoded).hexdigest()
    # insert user data
    client_internal = Clients(client_key="internal", client_secret=hash_pass, status="True", salt=salt)
    client_noninternal = Clients(client_key="noninternal", client_secret=hash_pass, status="False", salt=salt)
    db.session.add(client_internal)
    db.session.add(client_noninternal)
    db.session.commit()
    
    user = Users(name="andre", age=23, sex="male", client_id=1)
    book = Books(title="elektro", isbn=123456, writer="watt")
    db.session.add(user)
    db.session.add(book)
    db.session.commit()
    
    rent = Rent(book_id=1, user_id=1)
    db.session.add(rent)
    db.session.commit()

def create_token_internal():
    token = cache.get('test-token')
    if token is None:
    # prepare request input
        data = {
            'client_key': 'internal',
            'client_secret': 'password'
        }
        
        # do request 
        req = call_client(request)
        res = req.get('/token',
                       query_string=data)
        
        # store response
        res_json = json.loads(res.data)
        
        app.logger.warning('RESULT : %s', res_json)

        # assert / compare with expected result
        assert res.status_code == 200
        
        # save token into cache
        cache.set('test-token', res_json['token'], timeout=60)
        
        # return, because it usefull for other test
        return res_json['token']
    else:
        return token
    
def create_token_noninternal():
    token = cache.get('test-token')
    if token is None:
    # prepare request input
        data = {
            'client_key': 'noninternal',
            'client_secret': 'password'
        }
        
        # do request 
        req = call_client(request)
        res = req.get('/token',
                       query_string=data)
        
        # store response
        res_json = json.loads(res.data)
        
        app.logger.warning('RESULT : %s', res_json)

        # assert / compare with expected result
        assert res.status_code == 403
        
        # save token into cache
        cache.set('test-token', res_json['token'], timeout=60)
        
        # return, because it usefull for other test
        return res_json['token']
    else:
        return token