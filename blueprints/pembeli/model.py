from blueprints import db
from flask_restful import fields
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import text
from datetime import datetime

from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref


class Buyers(db.Model):
    __tablename__ = "buyers"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    alamat = db.Column(db.String(255))
    no_hp = db.Column(db.String(15))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    cart = db.relationship(
        'Carts', backref='buyers', lazy=True, uselist=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    response_fields = {
        'id': fields.Integer,
        'nama': fields.String,
        'email': fields.String,
        'alamat': fields.String,
        'no_hp': fields.String
    }

    def __init__(self, nama, email, alamat, no_hp):
        self.nama = nama
        self.email = email
        self.alamat = alamat
        self.no_hp = no_hp

    def __repr__(self):
        return '<Buyer %r>' % self.id
