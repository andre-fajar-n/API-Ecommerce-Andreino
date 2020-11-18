from flask_restful import Resource, reqparse, marshal
from blueprints import db, app, admin_required
from blueprints.models.sellers import SellerModel
from sqlalchemy import desc
import math

class AdminSellerResource(Resource):
    def options(self):
        return {'status': 'ok'}, 200

    @admin_required
    def delete(self, id):
        qry = SellerModel.query.get(id)
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

        qry = SellerModel.query
        total_data = qry.count()
        total_page = math.ceil(total_data/args["rp"])

        if args['orderby'] is not None:
            if args['orderby'] == 'nama':
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(SellerModel.id))
                else:
                    qry = qry.order_by(SellerModel.id)

        rows = []
        for row in qry.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, SellerModel.response_fields))

        app.logger.debug('DEBUG : %s', rows)

        return {
            "page": args["p"],
            "per_page": args["rp"],
            "total_page": total_page,
            "total_data": total_data,
            "data": rows,
        }, 200