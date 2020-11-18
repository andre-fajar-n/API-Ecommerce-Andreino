from blueprints.models.product_categories import ProductCategoryModel
from blueprints import admin_required, db, app
from flask_restful import Resource, marshal, reqparse

class AdminProductCategory(Resource):
    def options(self):
        return {'status': 'ok'}, 200

    @admin_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('tipe_produk', location='json', required=True)
        args = parser.parse_args()

        product_types = ProductCategoryModel(args['tipe_produk'])
        db.session.add(product_types)
        db.session.commit()

        app.logger.debug('DEBUG : %s', product_types)

        return marshal(product_types, ProductCategoryModel.response_fields), 200, {'Content-Type': 'application/json'}

    @admin_required
    def patch(self, id):
        qry = ProductCategoryModel.query.get(id)
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

        return marshal(qry, ProductCategoryModel.response_fields), 200, {'Content-Type': 'application/json'}

    @admin_required
    def delete(self, id):
        qry = ProductCategoryModel.query.get(id)
        if qry is None:
            app.logger.debug('DEBUG : id tidak ada')
            return {'status': 'NOT_FOUND'}, 404

        db.session.delete(qry)
        db.session.commit()

        app.logger.debug('DEBUG : data telah terhapus')

        return {'status': 'DELETED'}, 200