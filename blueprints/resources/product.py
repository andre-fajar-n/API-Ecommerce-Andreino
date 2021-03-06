from flask.blueprints import Blueprint
from flask_jwt_extended.utils import get_jwt_claims
from flask_restful import Api, Resource, marshal, reqparse
from sqlalchemy import desc
from blueprints import db, app, seller_required
from blueprints.models.product_categories import ProductCategoryModel
from blueprints.models.sellers import SellerModel
from blueprints.models.products import ProductModel
from flask_restful_swagger import swagger
import werkzeug
import uuid
import os

bp_product = Blueprint('product', __name__)
api = Api(bp_product)

class ProductSeller(Resource):
    def options(self):
        return {'status': 'ok'}, 200

    @seller_required
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
        product_type = ProductCategoryModel.query.filter_by(tipe_produk=args['kategori']).first()
        if product_type is None:
            app.logger.debug('DEBUG : kategori tidak ada')
            return {'message': 'kategori tidak ditemukan'}, 404

        # get seller id
        claims = get_jwt_claims()
        seller = SellerModel.query.filter_by(user_id=claims['id']).first()

        product = ProductModel(args['nama'],
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

        return marshal(product, ProductModel.response_fields), 200, {'Content-Type': 'application/json'}

    @seller_required
    def patch(self, id):
        qry = ProductModel.query.get(id)
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

            filename = ""
            if image_produk:
                randomstr = uuid.uuid4().hex  # get randum string to image filename
                filename = randomstr+'_'+image_produk.filename
                image_produk.save(os.path.join("."+UPLOAD_FOLDER, filename))
                img_path = UPLOAD_FOLDER.replace('./', '/')+'/'+filename
            qry.gambar = filename

        if args['kategori'] is not None:
            # get id dari product type yang kita input
            product_type = ProductCategoryModel.query.filter_by(tipe_produk=args['kategori']).first()
            if product_type is None:
                app.logger.debug('DEBUG : kategori tidak ada')
                return {'message': 'kategori tidak ditemukan'}, 404

        db.session.commit()

        app.logger.debug('DEBUG : %s', qry)

        return marshal(qry, ProductModel.response_fields), 200, {'Content-Type': 'application/json'}

    @seller_required
    def delete(self, id):
        qry = ProductModel.query.get(id)
        if qry is None:
            app.logger.debug('DEBUG : id tidak ada')
            return {'status': 'NOT_FOUND'}, 404

        db.session.delete(qry)
        db.session.commit()

        app.logger.debug('DEBUG : data telah terhapus')

        return {'status': 'DELETED'}, 200
    
    @seller_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=25)
        args = parser.parse_args()
        
        claims = get_jwt_claims()
        
        seller = SellerModel.query.filter_by(user_id=claims['id']).first()
        
        offset = (args['p'] * args['rp'] - args['rp'])

        qry = ProductModel.query.filter_by(seller_id=seller.id)
        qry = qry.order_by(desc(ProductModel.created_at))
        qry = qry.order_by(desc(ProductModel.updated_at))
        
        rows = []
        for row in qry.limit(args['rp']).offset(offset).all():
            marshal_row = marshal(row, ProductModel.response_fields)
            rows.append(marshal_row)

        app.logger.debug('DEBUG : %s', rows)

        return rows, 200

class ProductUser(Resource):
    def options(self):
        return {'status': 'ok'}, 200

    def get(self, id):
        qry = ProductModel.query.get(id)
        if qry is not None:
            app.logger.debug('DEBUG : %s', qry)
            return marshal(qry, ProductModel.response_fields), 200

        app.logger.debug('DEBUG : id tidak ada')
        return {'status': 'ID produk tidak ditemukan'}, 404


class ProductUserAll(Resource):
    def options(self):
        return {'status': 'ok'}, 200

    @swagger.operation(notes='some really good notes')
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=25)
        parser.add_argument('orderby', location='args',help='invalid orderby value', choices=('nama'))
        parser.add_argument('sort', location='args',help='invalid sort value', choices=('desc', 'asc'))
        args = parser.parse_args()

        offset = (args['p'] * args['rp'] - args['rp'])

        qry = ProductModel.query
        qry = qry.order_by(desc(ProductModel.created_at))
        qry = qry.order_by(desc(ProductModel.updated_at))

        if args['orderby'] is not None:
            if args['orderby'] == 'nama':
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(ProductModel.id))
                else:
                    qry = qry.order_by(ProductModel.id)

        rows = []
        for row in qry.limit(args['rp']).offset(offset).all():
            marshal_row = marshal(row, ProductModel.response_fields)
            seller = SellerModel.query.get(row.seller_id)
            marshal_seller = marshal(seller, SellerModel.response_fields)
            marshal_row['seller'] = marshal_seller
            rows.append(marshal_row)

        app.logger.debug('DEBUG : %s', rows)

        return rows, 200

api.add_resource(ProductSeller, '/seller', '/seller/<id>')
api.add_resource(ProductUser, '/<id>')
api.add_resource(ProductUserAll, '')