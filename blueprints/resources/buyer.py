from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal, inputs
from flask_jwt_extended import get_jwt_claims, jwt_required
import json
from blueprints.models.buyers import Buyers
from blueprints import db, app, internal_required, admin_required
from sqlalchemy import desc

bp_buyer = Blueprint('buyer', __name__)
api = Api(bp_buyer)

class Buyer(Resource):
    def options(self):
        return {'status': 'ok'}, 200

    @internal_required
    def post(self):
        claims = get_jwt_claims()
        parser = reqparse.RequestParser()
        parser.add_argument('name', location='json', default="")
        parser.add_argument('email', location='json', default="")
        parser.add_argument('address', location='json', default="")
        parser.add_argument('phone_number', location='json', default="")
        args = parser.parse_args()

        buyer = Buyers(args['name'], args['email'], args['address'], args['phone_number'], claims['id'])
        db.session.add(buyer)
        db.session.commit()

        app.logger.debug('DEBUG : %s', buyer)

        return marshal(buyer, Buyers.response_fields), 200, {'Content-Type': 'application/json'}

    @internal_required
    def get(self):
        claims = get_jwt_claims()
        qry = Buyers.query.filter_by(user_id=claims['id']).first()
        if qry is not None:
            app.logger.debug('DEBUG : %s', qry)
            return marshal(qry, Buyers.response_fields), 200

        app.logger.debug('DEBUG : biodata tidak ada')
        return {'status': 'biodata tidak ada'}, 404

    @internal_required
    def patch(self):
        claims = get_jwt_claims()
        qry = Buyers.query.filter_by(user_id=claims['id']).first()
        if qry is None:
            app.logger.debug('DEBUG : biodata tidak ada')
            return {'status': 'biodata tidak ada'}, 404

        parser = reqparse.RequestParser()
        parser.add_argument('name', location='json')
        parser.add_argument('email', location='json')
        parser.add_argument('address', location='json')
        parser.add_argument('phone_number', location='json')
        args = parser.parse_args()

        if args['name'] is not None:
            qry.nama = args['name']

        if args['email'] is not None:
            qry.email = args['email']

        if args['address'] is not None:
            qry.alamat = args['address']

        if args['phone_number'] is not None:
            qry.no_hp = args['phone_number']

        db.session.commit()

        app.logger.debug('DEBUG : %s', qry)

        return marshal(qry, Buyers.response_fields), 200, {'Content-Type': 'application/json'}

api.add_resource(Buyer, '')
