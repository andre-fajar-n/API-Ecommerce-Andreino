from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal, inputs
from flask_jwt_extended import get_jwt_claims, jwt_required
import json
from .model import Products
from blueprints.kategori_produk.model import ProductCategories
from blueprints.penjual.model import Sellers
from blueprints import db, app, internal_required, penjual_required, admin_required
from sqlalchemy import desc

bp_product = Blueprint('product', __name__)
api = Api(bp_product)


class ProductSeller(Resource):

    @penjual_required
    @jwt_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('nama', location='json', required=True)
        parser.add_argument('harga', location='json', required=True)
        parser.add_argument('stok', location='json', required=True)
        parser.add_argument('berat', location='json', required=True)
        parser.add_argument('deskripsi', location='json')
        parser.add_argument('gambar', location='json', required=True)
        parser.add_argument('kategori', location='json')
        args = parser.parse_args()

        # get id dari product type yang kita input
        product_type = ProductCategories.query.filter_by(
            tipe_produk=args['kategori'])
        if product_type is None:
            app.logger.debug('DEBUG : kategori tidak ada')
            return {'message': 'kategori tidak ditemukan'}, 404

        # get seller id
        claims = get_jwt_claims()
        seller = Sellers.query.filter_by(user_id=claims['id']).first()

        product = Products(args['nama'], args['harga'], args['stok'],
                           args['berat'], args['deskripsi'], args['gambar'], product_type.id, seller.id)
        db.session.add(product)
        db.session.commit()

        app.logger.debug('DEBUG : %s', product)

        return marshal(product, Products.response_fields), 200, {'Content-Type': 'application/json'}

    # @penjual_required
    def get(self, id):
        qry = Products.query.get(id)
        if qry is not None:
            app.logger.debug('DEBUG : %s', qry)
            return marshal(qry, Products.response_fields), 200

        app.logger.debug('DEBUG : id tidak ada')
        return {'status': 'NOT_FOUND'}, 404

    @penjual_required
    def patch(self, id):
        qry = Products.query.get(id)
        if qry is None:
            app.logger.debug('DEBUG : id tidak ada')
            return {'status': 'NOT_FOUND'}, 404

        parser = reqparse.RequestParser()
        parser.add_argument('nama', location='json')
        parser.add_argument('harga', location='json')
        parser.add_argument('stok', location='json')
        parser.add_argument('berat', location='json')
        parser.add_argument('deskripsi', location='json')
        parser.add_argument('gambar', location='json')
        parser.add_argument('kategori', location='json')
        args = parser.parse_args()

        # get id dari product type yang kita input
        product_type = ProductCategories.query.filter_by(
            tipe_produk=args['kategori'])
        if product_type is None:
            app.logger.debug('DEBUG : kategori tidak ada')
            return {'message': 'kategori tidak ditemukan'}, 404

        if args['nama'] is not None:
            qry.nama = args['nama']
        if args['harga'] is not None:
            qry.harga = args['harga']
        if args['stok'] is not None:
            qry.stok = args['stok']
        if args['berat'] is not None:
            qry.berat = args['berat']
        if args['deskripsi'] is not None:
            qry.deskripsi = args['deskripsi']
        if args['gambar'] is not None:
            qry.gambar = args['gambar']
        if product_type is not None:
            qry.product_type_id = product_type.id

        db.session.commit()

        app.logger.debug('DEBUG : %s', qry)

        return marshal(qry, Products.response_fields), 200, {'Content-Type': 'application/json'}

    @penjual_required
    @admin_required
    def delete(self, id):
        qry = Products.query.get(id)
        if qry is None:
            app.logger.debug('DEBUG : id tidak ada')
            return {'status': 'NOT_FOUND'}, 404

        db.session.delete(qry)
        db.session.commit()

        app.logger.debug('DEBUG : data telah terhapus')

        return {'status': 'DELETED'}, 200


class ProductList(Resource):

    # @internal_required
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

        qry = Products.query

        if args['orderby'] is not None:
            if args['orderby'] == 'nama':
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(Products.id))
                else:
                    qry = qry.order_by(Products.id)

        rows = []
        for row in qry.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, Products.response_fields))

        app.logger.debug('DEBUG : %s', rows)

        return rows, 200


api.add_resource(ProductList, '', '/list')
api.add_resource(ProductSeller, '', '/<id>')
