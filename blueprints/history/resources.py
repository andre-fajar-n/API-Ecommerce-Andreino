from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal, inputs
from flask_jwt_extended import get_jwt_claims, jwt_required
import json
from blueprints.keranjang.model import Carts
from blueprints.pembeli.model import Buyers
from blueprints.penjual.model import Sellers
from blueprints.produk.model import Products
from blueprints.detail_transaksi.model import TransactionDetails
from blueprints import db, app, internal_required, penjual_required, admin_required
from sqlalchemy import desc

bp_history = Blueprint('history', __name__)
api = Api(bp_history)

class HistoryBuyer(Resource):
    def options(self):
        return {'status':'ok'}, 200
    
    @internal_required
    def get(self):
        claims = get_jwt_claims()
        # filter tabel buyer berdasarkan user yang sedang login
        buyer = Buyers.query.filter_by(user_id=claims['id']).first()

        # filter tabel cart berdasarkan id pembeli dan status checkout nya true
        # kemudian diurutkan dari yang paling baru
        cart = Carts.query.filter_by(buyer_id=buyer.id)
        cart = cart.filter_by(status_checkout=True)
        cart = cart.order_by(desc(Carts.updated_at))
        
        # memasukkan data di tabel cart ke dalam list
        result = []
        for qry in cart:
            # memasukkan data penjual
            seller = Sellers.query.filter_by(id=qry.seller_id).first()
            marshal_seller = marshal(seller, Sellers.response_fields)
            marshal_qry = marshal(qry, Carts.response_fields)
            marshal_qry['seller_id'] = marshal_seller
            
            
            transaction_detail = TransactionDetails.query.filter_by(cart_id=qry.id)
            transaction_detail = transaction_detail.all()
            list_td = []
            for td in transaction_detail:
                product = Products.query.filter_by(id=td.product_id).first()
                marshal_product = marshal(product, Products.response_fields)
                marshal_td = marshal(td, TransactionDetails.response_fields)
                marshal_td['product_id'] = marshal_product
                list_td.append(marshal_td)
            result.append({'cart': marshal_qry, 'transaction_detail': list_td})
        return result, 200
    
api.add_resource(HistoryBuyer, '')