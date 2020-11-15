from blueprints import db
from flask_restful import fields
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import text
from datetime import datetime

from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref

class Carts(db.Model):
    __tablename__ = "carts"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    total_harga = db.Column(db.Integer, default=0)
    total_kuantitas = db.Column(db.Integer, default=0)
    ongkir = db.Column(db.Integer, default=0)
    status_checkout = db.Column(db.Boolean, default=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.id'))
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyers.id'))
    products = db.relationship('TransactionDetails', backref='carts', lazy=True, uselist=False)
    created_at = db.Column(db.DateTime(timezone=True),server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    response_fields = {
        'id': fields.Integer,
        'total_harga': fields.Integer,
        'total_kuantitas': fields.Integer,
        'ongkir': fields.Integer,
        'seller_id': fields.Integer,
        'buyer_id': fields.Integer,
        'status_checkout':fields.Boolean,
        'updated_at': fields.DateTime,
        'created_at': fields.DateTime,
    }

    def __init__(self, seller_id, buyer_id):
        self.seller_id = seller_id
        self.buyer_id = buyer_id

    def __repr__(self):
        return '<Products %r>' % self.id
