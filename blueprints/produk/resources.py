from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal, inputs
from flask_jwt_extended import get_jwt_claims, jwt_required
import json
import werkzeug
import os
import uuid
from .model import Products
from blueprints.kategori_produk.model import ProductCategories
from blueprints.penjual.model import Sellers
from blueprints import db, app, internal_required, penjual_required, admin_required
from sqlalchemy import desc

bp_product = Blueprint('product', __name__)
api = Api(bp_product)


class ProductSeller(Resource):
    def options(self):
        return {'status': 'ok'}, 200

    @penjual_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('nama', location='form', required=True)
        parser.add_argument('harga', location='form', required=True)
        parser.add_argument('stok', location='form')
        parser.add_argument('berat', location='form', required=True)
        parser.add_argument('deskripsi', location='form')
        parser.add_argument('gambar', type=werkzeug.datastructures.FileStorage, location='files')
        parser.add_argument('kategori', location='form')
        args = parser.parse_args()

        UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
        if args['gambar'] == "":
            return {'data': '', 'message': 'No file found', 'status': 'error'}, 500

        image_produk = args['gambar']

        if image_produk:
            randomstr = uuid.uuid4().hex  # get randum string to image filename
            filename = randomstr+'_'+image_produk.filename
            image_produk.save(os.path.join("."+UPLOAD_FOLDER, filename))
            img_path = UPLOAD_FOLDER.replace('./', '/')+'/'+filename

        else:
            return {'data': '', 'message': 'Something when wrong', 'status': 'error'}, 500

        # get id dari product type yang kita input
        product_type = ProductCategories.query.filter_by(tipe_produk=args['kategori']).first()
        if product_type is None:
            app.logger.debug('DEBUG : kategori tidak ada')
            return {'message': 'kategori tidak ditemukan'}, 404

        # get seller id
        claims = get_jwt_claims()
        seller = Sellers.query.filter_by(user_id=claims['id']).first()

        product = Products(args['nama'],
                           args['harga'],
                           args['stok'],
                           args['berat'],
                           args['deskripsi'],
                           filename,
                           product_type.id,
                           seller.id)
        db.session.add(product)
        db.session.commit()

        app.logger.debug('DEBUG : %s', product)

        return marshal(product, Products.response_fields), 200, {'Content-Type': 'application/json'}

    @penjual_required
    def patch(self, id):
        qry = Products.query.get(id)
        if qry is None:
            app.logger.debug('DEBUG : id tidak ada')
            return {'status': 'NOT_FOUND'}, 404

        parser = reqparse.RequestParser()
        parser.add_argument('nama', location='form')
        parser.add_argument('harga', location='form')
        parser.add_argument('stok', location='form')
        parser.add_argument('berat', location='form')
        parser.add_argument('deskripsi', location='form')
        parser.add_argument('gambar', type=werkzeug.datastructures.FileStorage, location='files')
        parser.add_argument('kategori', location='form')
        args = parser.parse_args()

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
            UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']

            image_produk = args['gambar']

            if image_produk:
                randomstr = uuid.uuid4().hex  # get randum string to image filename
                filename = randomstr+'_'+image_produk.filename
                image_produk.save(os.path.join("."+UPLOAD_FOLDER, filename))
                img_path = UPLOAD_FOLDER.replace('./', '/')+'/'+filename
            qry.gambar = filename

        if args['kategori'] is not None:
            # get id dari product type yang kita input
            product_type = ProductCategories.query.filter_by(tipe_produk=args['kategori']).first()
            if product_type is None:
                app.logger.debug('DEBUG : kategori tidak ada')
                return {'message': 'kategori tidak ditemukan'}, 404

        db.session.commit()

        app.logger.debug('DEBUG : %s', qry)

        return marshal(qry, Products.response_fields), 200, {'Content-Type': 'application/json'}

    @penjual_required
    def delete(self, id):
        qry = Products.query.get(id)
        if qry is None:
            app.logger.debug('DEBUG : id tidak ada')
            return {'status': 'NOT_FOUND'}, 404

        db.session.delete(qry)
        db.session.commit()

        app.logger.debug('DEBUG : data telah terhapus')

        return {'status': 'DELETED'}, 200
    
    @penjual_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=25)
        args = parser.parse_args()
        
        claims = get_jwt_claims()
        
        seller = Sellers.query.filter_by(user_id=claims['id']).first()
        
        offset = (args['p'] * args['rp'] - args['rp'])

        qry = Products.query.filter_by(seller_id=seller.id)
        qry = qry.order_by(desc(Products.created_at))
        qry = qry.order_by(desc(Products.updated_at))
        
        rows = []
        for row in qry.limit(args['rp']).offset(offset).all():
            marshal_row = marshal(row, Products.response_fields)
            rows.append(marshal_row)

        app.logger.debug('DEBUG : %s', rows)

        return rows, 200

# class ProductUser(Resource):
#     def options(self):
#         return {'status': 'ok'}, 200

#     def get(self, id):
#         qry = Products.query.get(id)
#         if qry is not None:
#             app.logger.debug('DEBUG : %s', qry)
#             return marshal(qry, Products.response_fields), 200

#         app.logger.debug('DEBUG : id tidak ada')
#         return {'status': 'ID produk tidak ditemukan'}, 404


# class ProductUserAll(Resource):
#     def options(self):
#         return {'status': 'ok'}, 200

#     def get(self):
#         parser = reqparse.RequestParser()
#         parser.add_argument('p', type=int, location='args', default=1)
#         parser.add_argument('rp', type=int, location='args', default=25)
#         parser.add_argument('orderby', location='args',help='invalid orderby value', choices=('nama'))
#         parser.add_argument('sort', location='args',help='invalid sort value', choices=('desc', 'asc'))
#         args = parser.parse_args()

#         offset = (args['p'] * args['rp'] - args['rp'])

#         qry = Products.query
#         qry = qry.order_by(desc(Products.created_at))
#         qry = qry.order_by(desc(Products.updated_at))

#         if args['orderby'] is not None:
#             if args['orderby'] == 'nama':
#                 if args['sort'] == 'desc':
#                     qry = qry.order_by(desc(Products.id))
#                 else:
#                     qry = qry.order_by(Products.id)

#         rows = []
#         for row in qry.limit(args['rp']).offset(offset).all():
#             marshal_row = marshal(row, Products.response_fields)
#             seller = Sellers.query.get(row.seller_id)
#             marshal_seller = marshal(seller, Sellers.response_fields)
#             marshal_row['seller'] = marshal_seller
#             rows.append(marshal_row)

#         app.logger.debug('DEBUG : %s', rows)

#         return rows, 200


# class ProductAdmin(Resource):
#     def options(self):
#         return {'status': 'ok'}, 200

#     @admin_required
#     def delete(self, id):
#         qry = Products.query.get(id)
#         if qry is None:
#             app.logger.debug('DEBUG : id tidak ada')
#             return {'status': 'NOT_FOUND'}, 404

#         db.session.delete(qry)
#         db.session.commit()

#         app.logger.debug('DEBUG : data telah terhapus')

#         return {'status': 'DELETED'}, 200


api.add_resource(ProductSeller, '')
# api.add_resource(ProductUser, '/<id>')
# api.add_resource(ProductUserAll, '')
# api.add_resource(ProductAdmin, '/admin/<id>')
