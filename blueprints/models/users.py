from blueprints import db
from flask_restful import fields
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import text
from datetime import datetime

from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(255))
    salt = db.Column(db.String(255))
    status_internal = db.Column(db.Boolean, nullable=False)
    status_penjual = db.Column(db.Boolean, nullable=False, default=False)
    status_admin = db.Column(db.Boolean, nullable=False, default=False)
    buyers = db.relationship('Buyers', backref='users',lazy=True, uselist=False)
    sellers = db.relationship('Sellers', backref='users', lazy=True, uselist=False)
    created_at = db.Column(db.DateTime(timezone=True),server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    response_fields = {
        'id': fields.Integer,
        'username': fields.String,
        'password': fields.String,
        'status_internal': fields.Boolean,
        'status_penjual': fields.Boolean,
        'status_admin': fields.Boolean
    }

    jwt_client_fields = {
        'id': fields.Integer,
        'username': fields.String,
        'status_internal': fields.Boolean,
        'status_penjual': fields.Boolean,
        'status_admin': fields.Boolean,
    }

    def __init__(self, username, password, salt, status_internal, status_penjual, status_admin):
        self.username = username
        self.password = password
        self.status_internal = status_internal
        self.status_penjual = status_penjual
        self.status_admin = status_admin
        self.salt = salt

    def __repr__(self):
        return '<User %r>' % self.id
