from blueprints import db
from flask_restful import fields
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import text
from datetime import datetime

from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref


class ProductCategorieModel(db.Model):
    __tablename__ = "product_types"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipe_produk = db.Column(db.String(50), nullable=False)
    products = db.relationship(
        'Products', backref='product_types', lazy=True, uselist=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    response_fields = {
        'id': fields.Integer,
        'tipe_produk': fields.String,
    }

    def __init__(self, tipe_produk):
        self.tipe_produk = tipe_produk

    def __repr__(self):
        return '<ProductCategories %r>' % self.id
