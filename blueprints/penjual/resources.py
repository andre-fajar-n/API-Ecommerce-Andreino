from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal, inputs
from flask_jwt_extended import get_jwt_claims, jwt_required
import json
from .model import Sellers
from blueprints import db, app, internal_required, penjual_required, admin_required
from sqlalchemy import desc

bp_seller = Blueprint('seller', __name__)
api = Api(bp_seller)


class SellerResource(Resource):

    @penjual_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('nama', location='json', required=True)
        parser.add_argument('email', location='json', required=True)
        parser.add_argument('alamat', location='json', required=True)
        parser.add_argument('no_hp', location='json', required=True)
        args = parser.parse_args()

        seller = Sellers(args['nama'], args['email'],
                         args['alamat'], args['no_hp'])
        db.session.add(seller)
        db.session.commit()

        app.logger.debug('DEBUG : %s', seller)

        return marshal(seller, Sellers.response_fields), 200, {'Content-Type': 'application/json'}

    @penjual_required
    def get(self):
        claims = get_jwt_claims()
        qry = Sellers.query.filter_by(user_id=claims['id']).first()
        if qry is not None:
            app.logger.debug('DEBUG : %s', qry)
            return marshal(qry, Sellers.response_fields), 200

        app.logger.debug('DEBUG : biodata tidak ada')
        return {'status': 'biodata tidak ada'}, 404

    @penjual_required
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


class SellerList(Resource):

    @admin_required
    def delete(self, id):
        qry = Sellers.query.get(id)
        if qry is None:
            app.logger.debug('DEBUG : id tidak ada')
            return {'status': 'NOT_FOUND'}, 404

        db.session.delete(qry)
        db.session.commit()

        app.logger.debug('DEBUG : data telah terhapus')

        return {'status': 'DELETED'}, 200

    @admin_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=25)
        parser.add_argument('orderby', location='args',
                            help='invalid orderby value', choices=('nama'))
        parser.add_argument('sort', location='args',
                            help='invalid sort value', choices=('desc', 'asc'))

        args = parser.parse_args()

        offset = (args['p'] * args['rp'] - args['rp'])

        qry = Sellers.query

        if args['orderby'] is not None:
            if args['orderby'] == 'nama':
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(Sellers.id))
                else:
                    qry = qry.order_by(Sellers.id)

        rows = []
        for row in qry.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, Sellers.response_fields))

        app.logger.debug('DEBUG : %s', rows)

        return rows, 200


api.add_resource(SellerList, '/admin/<id>', '/admin')
api.add_resource(SellerResource, '', '/user')
