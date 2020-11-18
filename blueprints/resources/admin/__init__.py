from blueprints.resources.admin.product_category import AdminProductCategory
from blueprints.resources.admin.product import AdminProductResource
from blueprints.resources.admin.seller import AdminSellerResource
from blueprints.resources.admin.buyer import AdminBuyerResource
from blueprints.resources.admin.user import AdminUserResource
from flask.blueprints import Blueprint
from flask_restful import Api

bp_admin = Blueprint('admin', __name__)
api = Api(bp_admin)

api.add_resource(AdminUserResource, "/user", "/user/<id>")
api.add_resource(AdminBuyerResource, "/buyer", "/buyer/<id>")
api.add_resource(AdminSellerResource, "/seller", "/seller/<id>")
api.add_resource(AdminProductResource, "/product/<id>")
api.add_resource(AdminProductCategory, "/product_category/<id>")