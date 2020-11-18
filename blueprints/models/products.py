from blueprints import db
from flask_restful import fields
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import text
from datetime import datetime

from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref


class ProductModel(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama = db.Column(db.String(255), nullable=False)
    harga = db.Column(db.Integer)
    stok = db.Column(db.Integer)
    berat = db.Column(db.Integer, default=0)
    deskripsi = db.Column(db.Text)
    gambar = db.Column(db.String(255), default="")
    product_type_id = db.Column(db.Integer, db.ForeignKey('product_types.id'))
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.id'))
    products = db.relationship('TransactionDetails', backref='products', lazy=True, uselist=False)
    created_at = db.Column(db.DateTime(timezone=True),server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    response_fields = {
        'id': fields.Integer,
        'nama': fields.String,
        'harga': fields.Integer,
        'stok': fields.Integer,
        'berat': fields.Integer,
        'deskripsi': fields.String,
        'gambar': fields.String,
        'product_type_id': fields.Integer,
        'seller_id': fields.Integer,
        'created_at':fields.DateTime,
        'updated_at':fields.DateTime,
    }

    def __init__(self, nama, harga, stok, berat, deskripsi, gambar, product_type_id, seller_id):
        self.nama = nama
        self.harga = harga
        self.stok = stok
        self.berat = berat
        self.deskripsi = deskripsi
        self.gambar = gambar
        self.product_type_id = product_type_id
        self.seller_id = seller_id

    def __repr__(self):
        return '<Products %r>' % self.id
