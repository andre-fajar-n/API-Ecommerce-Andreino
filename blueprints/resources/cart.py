from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal
from flask_jwt_extended import get_jwt_claims
from blueprints.models.carts import CartModel
from blueprints.models.transaction_details import TransactionDetailModel
from blueprints.models.buyers import BuyerModel
from blueprints.models.products import ProductModel
from blueprints.models.sellers import SellerModel
from blueprints import db, app, internal_required

bp_cart = Blueprint('cart', __name__)
api = Api(bp_cart)

class CartsResource(Resource):
    def options(self):
        return {'status': 'ok'}, 200

    @internal_required
    def get(self):
        claims = get_jwt_claims()
        buyer = BuyerModel.query.filter_by(user_id=claims['id']).first()

        cart = CartModel.query.filter_by(buyer_id=buyer.id)
        cart = cart.filter_by(status_checkout=False)
        result = []
        for qry in cart:
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

    @internal_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('product_id', location='args', type=int)
        parser.add_argument('quantity', location='args', type=int)
        args = parser.parse_args()

        # cek produk ada atau tidak
        product = ProductModel.query.get(args['product_id'])
        if product is None:
            app.logger.debug('DEBUG : produk tidak ada')
            return {'status': 'NOT_FOUND', 'message': 'produk tidak ada'}, 404

        # cek apakah produk sudah masuk di keranjang
        # jika belum, seller_id dan user_id ditambah ke keranjang
        # jika sudah, nilai kuantitas dan harga diupdate
        claims = get_jwt_claims()
        buyer = BuyerModel.query.filter_by(user_id=claims['id']).first()
        cart = CartModel.query.filter_by(buyer_id=buyer.id)
        cart = cart.filter_by(status_checkout=False)
        cart = cart.filter_by(seller_id=product.seller_id).first()

        if cart is None:
            cart = CartModel(product.seller_id, buyer.id)
            db.session.add(cart)
            db.session.commit()

        update_total_kuantitas = 0
        update_total_harga = 0
        transactionDetail = TransactionDetailModel.query.filter_by(cart_id=cart.id)
        if transactionDetail is None:
            transactionDetail = TransactionDetailModel(product.harga*args['quantity'], args['quantity'], cart.id, args['product_id'])
            db.session.add(transactionDetail)
            db.session.commit()
        else:
            transactionDetail = transactionDetail.filter_by(product_id=args['product_id']).first()
            if transactionDetail is None:
                transactionDetail = TransactionDetailModel(product.harga*args['quantity'], args['quantity'], cart.id, args['product_id'])
                db.session.add(transactionDetail)

                update_total_kuantitas = args['quantity']
                update_total_harga = args['quantity']*product.harga
                db.session.commit()
            else:
                update_total_kuantitas = args['quantity'] - transactionDetail.kuantitas
                update_total_harga = (args['quantity']*product.harga) - transactionDetail.harga

                transactionDetail.kuantitas = args['quantity']
                transactionDetail.harga = args['quantity']*product.harga
                db.session.commit()

        cart.total_kuantitas += update_total_kuantitas
        cart.total_harga += update_total_harga
        db.session.commit()

        app.logger.debug('DEBUG: sukses')
        return {'status': 'sukses'}, 200

    @internal_required
    def delete(self, id):
        claims = get_jwt_claims()
        buyer = BuyerModel.query.filter_by(user_id=claims['id']).first()
        if buyer is None:
            app.logger.debug('DEBUG : pembeli tidak ada')
            return {'status': 'NOT_FOUND', 'message': 'pembeli tidak ada'}, 404
        cart = CartModel.query.filter_by(buyer_id=buyer.id)
        cart = cart.filter_by(status_checkout=False)

        transactionDetail = TransactionDetailModel.query.get(id)
        cart = CartModel.query.get(transactionDetail.cart_id)

        cart.total_kuantitas -= transactionDetail.kuantitas
        cart.total_harga -= transactionDetail.harga

        if cart.total_kuantitas == 0:
            db.session.delete(cart)

        db.session.delete(transactionDetail)
        db.session.commit()

        app.logger.debug('DEBUG : data telah terhapus')

        return {'status': 'DELETED'}, 200

api.add_resource(CartsResource, '', '/<id>')
