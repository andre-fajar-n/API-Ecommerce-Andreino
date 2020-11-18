from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal
from blueprints.models.product_categories import ProductCategoryModel
from sqlalchemy import desc

bp_product_categories = Blueprint('product_categories', __name__)
api = Api(bp_product_categories)
    
class ProductTypeUserList(Resource):
    def options(self):
        return {'status': 'ok'}, 200
    
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=25)
        parser.add_argument('orderby', location='args', help='invalid orderby value', choices=('tipe_produk'))
        parser.add_argument('sort', location='args', help='invalid sort value', choices=('desc', 'asc'))

        args = parser.parse_args()

        offset = (args['p'] * args['rp'] - args['rp'])

        qry = ProductCategoryModel.query

        if args['orderby'] is not None:
            if args['orderby'] == 'tipe_produk':
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(ProductCategoryModel.id))
                else:
                    qry = qry.order_by(ProductCategoryModel.id)

        rows = []
        for row in qry.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, ProductCategoryModel.response_fields))

        return rows, 200

api.add_resource(ProductTypeUserList, '')
