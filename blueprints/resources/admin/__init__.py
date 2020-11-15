from blueprints.resources.admin.buyer import AdminBuyer
from blueprints.resources.admin.user import AdminUser
from flask.blueprints import Blueprint
from flask_restful import Api

bp_admin = Blueprint('admin', __name__)
api = Api(bp_admin)

api.add_resource(AdminUser, "/user", "/user/<id>")
api.add_resource(AdminBuyer, "/buyer", "/buyer/<id>")