from blueprints import db, app, seller_required
from blueprints.models.sellers import Sellers
from flask import Blueprint
from flask_jwt_extended.utils import get_jwt_claims
from flask_restful import Api, Resource, marshal, reqparse

bp_seller = Blueprint('seller', __name__)
api = Api(bp_seller)


class Seller(Resource):
    def options(self):
        return {'status': 'ok'}, 200

    @seller_required
    def post(self):
        claims = get_jwt_claims()
        parser = reqparse.RequestParser()
        parser.add_argument('nama', location='json', required=True)
        parser.add_argument('email', location='json', required=True)
        parser.add_argument('alamat', location='json', required=True)
        parser.add_argument('no_hp', location='json', required=True)
        args = parser.parse_args()

        seller = Sellers(args['nama'], args['email'],args['alamat'], args['no_hp'], claims['id'])
        db.session.add(seller)
        db.session.commit()

        app.logger.debug('DEBUG : %s', seller)

        return marshal(seller, Sellers.response_fields), 200, {'Content-Type': 'application/json'}

    @seller_required
    def get(self):
        claims = get_jwt_claims()
        qry = Sellers.query.filter_by(user_id=claims['id']).first()
        print("cek", qry)
        if qry is not None:
            app.logger.debug('DEBUG : %s', qry)
            return marshal(qry, Sellers.response_fields), 200

        app.logger.debug('DEBUG : biodata tidak ada')
        return {'status': 'biodata tidak ada'}, 404

    @seller_required
    def patch(self):
        claims = get_jwt_claims()
        qry = Sellers.query.filter_by(user_id=claims['id']).first()
        if qry is None:
            app.logger.debug('DEBUG : biodata tidak ada')
            return {'status': 'biodata tidak ada'}, 404

        parser = reqparse.RequestParser()
        parser.add_argument('nama', location='json')
        parser.add_argument('email', location='json')
        parser.add_argument('alamat', location='json')
        parser.add_argument('no_hp', location='json')
        args = parser.parse_args()

        if args['nama'] is not None:
            qry.nama = args['nama']
        if args['email'] is not None:
            qry.email = args['email']
        if args['alamat'] is not None:
            qry.alamat = args['alamat']
        if args['no_hp'] is not None:
            qry.no_hp = args['no_hp']
        db.session.commit()

        app.logger.debug('DEBUG : %s', qry)

        return marshal(qry, Sellers.response_fields), 200, {'Content-Type': 'application/json'}

api.add_resource(Seller, "")