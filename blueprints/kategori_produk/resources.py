from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal, inputs
from flask_jwt_extended import get_jwt_claims
import json
from .model import ProductCategories
from blueprints import db, app, internal_required, penjual_required, admin_required
from sqlalchemy import desc

bp_product_categories = Blueprint('product_categories', __name__)
api = Api(bp_product_categories)


class ProductTypeResource(Resource):

    @admin_required
    @penjual_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('tipe_produk', location='json', required=True)
        args = parser.parse_args()

        product_types = ProductCategories(args['tipe_produk'])
        db.session.add(product_types)
        db.session.commit()

        app.logger.debug('DEBUG : %s', product_types)

        return marshal(product_types, ProductCategories.response_fields), 200, {'Content-Type': 'application/json'}

    # @internal_required
    def get(self, id):
        qry = ProductCategories.query.get(id)
        if qry is not None:
            app.logger.debug('DEBUG : %s', qry)
            return marshal(qry, ProductCategories.response_fields), 200

        app.logger.debug('DEBUG : id tidak ada')
        return {'status': 'NOT_FOUND'}, 404

    @internal_required
    @admin_required
    def patch(self, id):
        qry = ProductCategories.query.get(id)
        if qry is None:
            app.logger.debug('DEBUG : id tidak ada')
            return {'status': 'NOT_FOUND'}, 404

        parser = reqparse.RequestParser()
        parser.add_argument('tipe_produk', location='json')
        args = parser.parse_args()

        if args['tipe_produk'] is not None:
            qry.tipe_produk = args['tipe_produk']

        db.session.commit()

        app.logger.debug('DEBUG : %s', qry)

        return marshal(qry, ProductCategories.response_fields), 200, {'Content-Type': 'application/json'}

    @penjual_required
    @admin_required
    def delete(self, id):
        qry = ProductCategories.query.get(id)
        if qry is None:
            app.logger.debug('DEBUG : id tidak ada')
            return {'status': 'NOT_FOUND'}, 404

        db.session.delete(qry)
        db.session.commit()

        app.logger.debug('DEBUG : data telah terhapus')

        return {'status': 'DELETED'}, 200


class ProductTypeList(Resource):

    # @penjual_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=25)
        parser.add_argument('orderby', location='args',
                            help='invalid orderby value', choices=('tipe_produk'))
        parser.add_argument('sort', location='args',
                            help='invalid sort value', choices=('desc', 'asc'))

        args = parser.parse_args()

        offset = (args['p'] * args['rp'] - args['rp'])

        qry = ProductCategories.query

        if args['orderby'] is not None:
            if args['orderby'] == 'tipe_produk':
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(ProductCategories.id))
                else:
                    qry = qry.order_by(ProductCategories.id)

        rows = []
        for row in qry.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, ProductCategories.response_fields))

        return rows, 200


api.add_resource(ProductTypeList, '', '/list')
api.add_resource(ProductTypeResource, '', '/<id>')
