from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal, inputs
from flask_jwt_extended import get_jwt_claims, jwt_required
import json
from blueprints.keranjang.model import Carts
from blueprints.pembeli.model import Buyers
from blueprints import db, app, internal_required, penjual_required, admin_required
from sqlalchemy import desc

bp_checkout = Blueprint('checkout', __name__)
api = Api(bp_checkout)

class Checkout(Resource):
    def options(self):
        return {'status': 'ok'}, 200
    
    @internal_required
    def post(self):
        claims = get_jwt_claims()
        buyer = Buyers.query.filter_by(user_id=claims['id']).first()
        cart = Carts.query.filter_by(buyer_id=buyer.id)
        
        print("checkout", cart)
        for qry in cart:
            qry.status_checkout = True
            db.session.commit()
            
        return {'status': 'success'}, 200
    
api.add_resource(Checkout, '')