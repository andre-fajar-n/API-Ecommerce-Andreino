from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal, inputs
from flask_jwt_extended import get_jwt_claims, jwt_required
import json
from .model import Carts
from blueprints.detail_transaksi.model import TransactionDetails
from blueprints.pembeli.model import Buyers
from blueprints.produk.model import Products
from blueprints.penjual.model import Sellers
from blueprints import db, app, internal_required, penjual_required, admin_required
from sqlalchemy import desc

bp_cart = Blueprint('cart', __name__)
api = Api(bp_cart)


class Carts(Resource):

    @jwt_required
    def get(self):
        claims = get_jwt_claims()
        buyer = Buyers.query.filter_by(user_id=claims['id'])
        cart = Carts.query.filter_by(buyer_id=buyer.id)
        cart = cart.all()
        result = []
        for qry in cart:
            seller = Sellers.query.filter_by(id=qry.seller_id).first()
            marshal_seller = marshal(seller, Sellers.response_fields)
            marshal_qry = marshal(qry, Carts.response_fields)
            marshal_qry['seller_id'] = marshal_seller
            transaction_detail = TransactionDetails.query.filter_by(
                cart_id=qry.id)
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

    @jwt_required
    @internal_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('product_id', location='json')
        parser.add_argument('quantity', location='json')
        args = parser.parse_args()

        # cek produk ada atau tidak
        product = Products.query.get(args['product_id'])
        if product is None:
            app.logger.debug('DEBUG : produk tidak ada')
            return {'status': 'NOT_FOUND', 'message': 'produk tidak ada'}, 404

        # cek apakah produk sudah masuk di keranjang
        # jika belum, seller_id dan user_id ditambah ke keranjang
        # jika sudah, nilai kuantitas dan harga diupdate
        claims = get_jwt_claims()
        buyer = Buyers.query.filter_by(user_id=claims['id'])
        cart = Carts.query.filter_by(buyer_id=buyer.id).first()
        if cart is None:
            cart = Carts(product.seller_id, buyer.id)
            db.session.add(cart)
            db.session.commit()
            transaction_detail = TransactionDetails(
                product.harga * args['quantity'], args['quantity'], cart.id, args['product_id'])
            db.session.add(transaction_detail)
            db.session.commit()
        else:
            transaction_detail = TransactionDetails.query.filter_by(
                cart_id=cart.id)
            transaction_detail = transaction_detail.filter_by(
                product_id=args['product_id']).first()
            transaction_detail.kuantitas = args['quantity']
            transaction_detail.harga = product.harga * args['quantity']
            db.session.commit()

        cart.total_kuantitas += transaction_detail.kuantitas
        cart.total_harga += transaction_detail.harga

        db.session.commit()

        app.logger.debug('DEBUG: sukses')
        return {'status': 'sukses'}, 200

    # @internal_required
    # @jwt_required
    # def delete(self):
    #     claims = get_jwt_claims()
    #     buyer = Buyers.query.filter_by(user_id=claims['id'])
    #     cart = Carts.query.filter_by(buyer_id=buyer.id).first()
