import config
import json
import os

from functools import wraps
from flask_cors import CORS
from flask_jwt_extended import JWTManager, get_jwt_claims, verify_jwt_in_request
from flask import Flask, request, send_from_directory
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy

###############################################################
app = Flask(__name__)

# @app.route("/")
# def hello():
#     return {'pesan': 'masuk'}, 200

CORS(app, origins="*", allow_headers=[
    "Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
    supports_credentials=True, intercept_exceptions=False)

jwt = JWTManager(app)


def internal_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if not claims['status_internal']:  # hard code
            return {'status': 'FORBIDDEN', 'message': 'Internal Only!'}, 403
        else:
            return fn(*args, **kwargs)
    return wrapper

def penjual_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if not claims['status_penjual']:  # hard code
            return {'status': 'FORBIDDEN', 'message': 'Bukan penjual'}, 403
        else:
            return fn(*args, **kwargs)
    return wrapper


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if not claims['status_admin']:  # hard code
            return {'status': 'FORBIDDEN', 'message': 'Bukan admin'}, 403
        else:
            return fn(*args, **kwargs)
    return wrapper


my_flask = os.environ.get('FLASK_ENV', 'Production')
if my_flask == 'Production':
    app.config.from_object(config.ProductionConfig)
elif my_flask == 'Testing':
    app.config.from_object(config.TestingConfig)
else:
    app.config.from_object(config.DevelopmentConfig)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

@app.before_request
def before_request():
    filename = request.path.split('/')
    if request.method == "GET" and filename[1] == "img" : 
        return send_from_directory(".."+app.config['UPLOAD_FOLDER'], filename[2]), 200
    
@app.before_request
def before_request():
    if request.method != 'OPTIONS':  # <-- required
        pass
    else :
        return {}, 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*', 'Access-Control-Allow-Methods':'*'}

# log handler
@app.after_request
def after_request(response):
    try:
        requestData = request.get_json()
    except Exception as e:
        requestData = request.args.to_dict()
    ## dipake jadi trycatch soalnya response iamge ga bisa di decode json
    try : 
        if response.status_code == 200:
            app.logger.info("REQUEST_LOG\t%s",
                            json.dumps({
                                'status_code': response.status_code,
                                'method': request.method,
                                'code': response.status,
                                'uri': request.full_path,
                                'request': requestData,
                                'response': json.loads(response.data.decode('utf-8'))
                            })
                            )
        else:
            app.logger.error("REQUEST_LOG\t%s",
                            json.dumps({
                                'status_code': response.status_code,
                                'method': request.method,
                                'code': response.status,
                                'uri': request.full_path,
                                'request': requestData,
                                'response': json.loads(response.data.decode('utf-8'))
                            })
                            )
    except Exception as e:
        pass
    return response


# Import Blueprint
from blueprints.kategori_produk.resources import bp_product_categories
from blueprints.keranjang.resources import bp_cart
from blueprints.pembeli.resources import bp_buyer
from blueprints.penjual.resources import bp_seller
from blueprints.produk.resources import bp_product
from blueprints.token import bp_auth
from blueprints.user.resources import bp_user
from blueprints.checkout import bp_checkout
from blueprints.history.resources import bp_history

# Register Blueprint
app.register_blueprint(bp_product_categories, url_prefix='/kategori')
app.register_blueprint(bp_cart, url_prefix='/keranjang')
app.register_blueprint(bp_buyer, url_prefix='/pembeli')
app.register_blueprint(bp_seller, url_prefix='/penjual')
app.register_blueprint(bp_product, url_prefix='/produk')
app.register_blueprint(bp_auth, url_prefix='/login')
app.register_blueprint(bp_user, url_prefix='/user')
app.register_blueprint(bp_checkout, url_prefix='/checkout')
app.register_blueprint(bp_history, url_prefix="/history")

db.create_all()
