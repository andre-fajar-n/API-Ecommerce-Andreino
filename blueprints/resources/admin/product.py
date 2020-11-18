from flask_restful import Resource
from blueprints import admin_required, db, app
from blueprints.models.products import ProductModel

class AdminProductResource(Resource):
    def options(self):
        return {'status': 'ok'}, 200

    @admin_required
    def delete(self, id):
        qry = ProductModel.query.get(id)
        if qry is None:
            app.logger.debug('DEBUG : id tidak ada')
            return {'status': 'NOT_FOUND'}, 404

        db.session.delete(qry)
        db.session.commit()

        app.logger.debug('DEBUG : data telah terhapus')

        return {'status': 'DELETED'}, 200