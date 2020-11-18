from flask import Blueprint
from flask_restful import Resource, Api, marshal
from flask_jwt_extended import get_jwt_claims
from blueprints.models.carts import CartModel
from blueprints.models.buyers import BuyerModel
from blueprints.models.sellers import SellerModel
from blueprints.models.products import ProductModel
from blueprints.models.transaction_details import TransactionDetailModel
from blueprints import internal_required, seller_required
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
        buyer = BuyerModel.query.filter_by(user_id=claims['id']).first()

        # filter tabel cart berdasarkan id pembeli dan status checkout nya true
        # kemudian diurutkan dari yang paling baru
        cart = CartModel.query.filter_by(buyer_id=buyer.id)
        cart = cart.filter_by(status_checkout=True)
        cart = cart.order_by(desc(CartModel.updated_at))
        
        # memasukkan data di tabel cart ke dalam list
        result = []
        for qry in cart:
            # memasukkan data penjual
            seller = SellerModel.query.filter_by(id=qry.seller_id).first()
            marshal_seller = marshal(seller, SellerModel.response_fields)
            marshal_qry = marshal(qry, CartModel.response_fields)
            marshal_qry['seller_id'] = marshal_seller
            
            
            transaction_detail = TransactionDetailModel.query.filter_by(cart_id=qry.id)
            transaction_detail = transaction_detail.all()
            list_td = []
            for td in transaction_detail:
                product = ProductModel.query.filter_by(id=td.product_id).first()
                marshal_product = marshal(product, ProductModel.response_fields)
                marshal_td = marshal(td, TransactionDetailModel.response_fields)
                marshal_td['product_id'] = marshal_product
                list_td.append(marshal_td)
            result.append({'cart': marshal_qry, 'transaction_detail': list_td})
        return result, 200
    
class HistorySeller(Resource):
    def options(self):
        return {'status':'ok'}, 200
    
    @seller_required
    def get(self):
        claims = get_jwt_claims()
        # filter tabel buyer berdasarkan user yang sedang login
        seller = SellerModel.query.filter_by(user_id=claims['id']).first()

        # filter tabel cart berdasarkan id pembeli dan status checkout nya true
        # kemudian diurutkan dari yang paling baru
        cart = CartModel.query.filter_by(seller_id=seller.id)
        cart = cart.filter_by(status_checkout=True)
        cart = cart.order_by(desc(CartModel.updated_at))
        
        # memasukkan data di tabel cart ke dalam list
        result = []
        for qry in cart:
            # memasukkan data penjual
            buyer = BuyerModel.query.filter_by(id=qry.buyer_id).first()
            marshal_buyer = marshal(buyer, BuyerModel.response_fields)
            marshal_qry = marshal(qry, CartModel.response_fields)
            marshal_qry['buyer_id'] = marshal_buyer
            
            
            transaction_detail = TransactionDetailModel.query.filter_by(cart_id=qry.id)
            transaction_detail = transaction_detail.all()
            list_td = []
            for td in transaction_detail:
                product = ProductModel.query.filter_by(id=td.product_id).first()
                marshal_product = marshal(product, ProductModel.response_fields)
                marshal_td = marshal(td, TransactionDetailModel.response_fields)
                marshal_td['product_id'] = marshal_product
                list_td.append(marshal_td)
            result.append({'cart': marshal_qry, 'transaction_detail': list_td})
        return result, 200
    
api.add_resource(HistoryBuyer, '/buyer')
api.add_resource(HistorySeller, '/seller')