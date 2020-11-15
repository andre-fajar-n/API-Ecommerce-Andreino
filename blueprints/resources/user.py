from flask.blueprints import Blueprint
from flask_restful import Api, reqparse
from blueprints.models.users import Users
from flask_jwt_extended.utils import get_jwt_claims
from blueprints import db, app, internal_required
from flask_restful import Resource, marshal
import uuid
import hashlib

bp_user = Blueprint('user', __name__)
api = Api(bp_user)

class User(Resource):
    def options(self):
        return {'status': 'ok'}, 200

    @internal_required
    def get(self):
        claims = get_jwt_claims()
        qry = Users.query.get(claims["id"])
        if qry is not None:
            app.logger.debug('DEBUG : %s', qry)
            return marshal(qry, Users.response_fields), 200

        app.logger.debug('DEBUG : id tidak ada')
        return {'status': 'NOT_FOUND'}, 404

    @internal_required
    def patch(self):
        claims = get_jwt_claims()
        qry = Users.query.get(claims["id"])
        if qry is None:
            app.logger.debug('DEBUG : id tidak ada')
            return {'status': 'NOT_FOUND'}, 404

        parser = reqparse.RequestParser()
        parser.add_argument('username', location='json')
        parser.add_argument('password', location='json')
        parser.add_argument('status_penjual', location='json', type=bool)
        args = parser.parse_args()

        if args['username'] is not None:
            qry.username = args['username']
        
        if args['password'] is not None:
            salt = uuid.uuid4().hex
            encoded = ('%s%s' % (args['password'], salt)).encode('utf-8')
            hash_pass = hashlib.sha512(encoded).hexdigest()

            qry.password = hash_pass
            qry.salt = salt
        
        if args['status_penjual'] is not None:
            qry.status_penjual = args['status_penjual']
            
        db.session.commit()

        app.logger.debug('DEBUG : %s', qry)

        return marshal(qry, Users.response_fields), 200, {'Content-Type': 'application/json'}

api.add_resource(User, "")