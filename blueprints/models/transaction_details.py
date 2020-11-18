from blueprints import db
from flask_restful import fields
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import text
from datetime import datetime

from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref


class TransactionDetailModel(db.Model):
    __tablename__ = "transaction_details"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    harga = db.Column(db.Integer, default=0)
    kuantitas = db.Column(db.Integer, default=0)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    response_fields = {
        'id': fields.Integer,
        'harga': fields.Integer,
        'kuantitas': fields.Integer,
        'cart_id': fields.Integer,
        'product_id': fields.Integer,
    }

    def __init__(self, harga, kuantitas, cart_id, product_id):
        self.harga = harga
        self.kuantitas = kuantitas
        self.cart_id = cart_id
        self.product_id = product_id

    def __repr__(self):
        return '<TransactionDetails %r>' % self.id
