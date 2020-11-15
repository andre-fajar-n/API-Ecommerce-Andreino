from flask.blueprints import Blueprint
from flask_restful import Api
from blueprints.resources.admin.user import AdminUser

bp_admin = Blueprint('admin', __name__)
api = Api(bp_admin)

api.add_resource(AdminUser, "/user", "/user/<id>")