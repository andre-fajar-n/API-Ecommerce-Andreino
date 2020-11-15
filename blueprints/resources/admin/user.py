from flask_restful import marshal, reqparse
from blueprints import admin_required, db, app
from blueprints.models.users import Users
from flask_restful import Resource
from sqlalchemy import func, desc
import math

class AdminUser(Resource):
    def options(self):
        return {'status': 'ok'}, 200
    
    @admin_required
    def delete(self, id):
        qry = Users.query.get(id)
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
        parser.add_argument('orderby', location='args',help='invalid orderby value', choices=('username'))
        parser.add_argument('sort', location='args',help='invalid sort value', choices=('desc', 'asc'))

        args = parser.parse_args()

        offset = (args['p'] * args['rp'] - args['rp'])

        qry = Users.query
        total_data = qry.count()
        total_page = math.ceil(total_data/args["rp"])

        if args['orderby'] is not None:
            if args['orderby'] == 'username':
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(Users.id))
                else:
                    qry = qry.order_by(Users.id)

        rows = []

        for row in qry.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, Users.response_fields))

        return {
            "page": args["p"],
            "per_page": args["rp"],
            "total_page": total_page,
            "total_data": total_data,
            "data": rows,
        }, 200