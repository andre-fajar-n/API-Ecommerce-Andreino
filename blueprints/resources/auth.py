from flask.blueprints import Blueprint
from flask_jwt_extended.utils import create_access_token, get_jwt_claims, get_jwt_identity
from flask_jwt_extended.view_decorators import jwt_required
from blueprints import db, internal_required
from blueprints import app
from blueprints.models.users import Users
from flask_restful import Api, Resource, marshal
from flask_restful import reqparse
import hashlib
import uuid

bp_auth = Blueprint('auth', __name__)
api = Api(bp_auth)

class Register(Resource):
    def options(self):
        return {'status': 'ok'}, 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', location='json', required=True)
        parser.add_argument('password', location='json', required=True)
        parser.add_argument('status_internal', location='json', type=bool, default=True)
        parser.add_argument('status_penjual', location='json', type=bool)
        parser.add_argument('status_admin', location='json', type=bool)
        args = parser.parse_args()

        salt = uuid.uuid4().hex
        encoded = ('%s%s' % (args['password'], salt)).encode('utf-8')
        hash_pass = hashlib.sha512(encoded).hexdigest()

        user = Users(args['username'], hash_pass, salt, args['status_internal'], args['status_penjual'], args['status_admin'])
        db.session.add(user)
        db.session.commit()

        app.logger.debug('DEBUG : %s', user)

        return marshal(user, Users.response_fields), 200, {'Content-Type': 'application/json'}

class Login(Resource):
    def options(self):
        return {'status': 'ok'}, 200

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', location='args', required=True)
        parser.add_argument('password', location='args', required=True)
        args = parser.parse_args()

        qry_client = Users.query.filter_by(username=args['username']).first()

        result = {
            "message":{},
            "data":{}
        }
        if qry_client is not None:
            client_salt = qry_client.salt
            encoded = ('%s%s' %(args['password'], client_salt)).encode('utf-8')
            hash_pass = hashlib.sha512(encoded).hexdigest()
            if hash_pass == qry_client.password:
                qry_client = marshal(qry_client, Users.jwt_client_fields)
                token = create_access_token(identity=args['username'], user_claims=qry_client)

                result["message"]["en"] = "Login success"
                result["message"]["id"] = "Login sukses"
                result["data"]["token"] = token
                return result, 200
            
            else:
                result["message"]["en"] = "Wrong password"
                result["message"]["id"] = "Password salah"
                return result, 401

        result["message"]["en"] = "User not found"
        result["message"]["id"] = "User tidak ditemukan"
        return result, 404

class RefreshToken(Resource):
    def options(self):
        return {'status': 'ok'}, 200

    @internal_required
    @jwt_required
    def get(self):
        current_user = get_jwt_identity()
        claims = get_jwt_claims()
        token = create_access_token(identity=current_user, user_claims=claims)
        return {
            "data": {'token': token}
        }, 200

api.add_resource(Register, "/register")
api.add_resource(Login, "/login")
api.add_resource(RefreshToken, "/refresh_token")