from flask import Blueprint
from flask_restful import Resource, Api
from flask_jwt_extended import get_jwt_claims
from blueprints.models.carts import CartModel
from blueprints.models.buyers import BuyerModel
from blueprints import db, internal_required

bp_checkout = Blueprint('checkout', __name__)
api = Api(bp_checkout)

class Checkout(Resource):
    def options(self):
        return {'status': 'ok'}, 200
    
    @internal_required
    def post(self):
        claims = get_jwt_claims()
        buyer = BuyerModel.query.filter_by(user_id=claims['id']).first()
        cart = CartModel.query.filter_by(buyer_id=buyer.id)
        cart = cart.filter_by(status_checkout=False)
        
        for qry in cart:
            qry.status_checkout = True
            db.session.commit()
            
        return {'status': 'success'}, 200
    
api.add_resource(Checkout, '')