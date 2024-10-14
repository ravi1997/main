

from flask import jsonify,current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, func
from sqlalchemy.types import Enum as SQLAEnum
from sqlalchemy.orm import validates
from datetime import datetime
from app.default import AccountStatusEnum, YNEnum
from app.metamodel import RouteMeta
from app.extension import db, bcrypt


class BaseAttributes(RouteMeta):
    __abstract__ = True
    
    deleted = db.Column(SQLAEnum(YNEnum), nullable=False, server_default="NO")
    created_by = db.Column(db.Integer, nullable=False, index=True)
    created_date = db.Column(DateTime, server_default=func.now())
    updated_by = db.Column(db.Integer, nullable=False, index=True)
    updated_date = db.Column(DateTime, server_default=func.now())

    @validates('updated_by')
    def validate_updated_by(self, key, value):
        if value is not None:
            if value == 0:
                return value
        if value is not None and not db.session.query(Account.id).filter_by(id=value).first():
            raise ValueError(f"Invalid updated_by value: {value} does not exist.")
        return value
    
    @validates('created_by')
    def validate_created_by(self, key, value):
        if value is not None:
            if value == 0:
                return value
        if value is not None and not db.session.query(Account.id).filter_by(id=value).first():
            raise ValueError(f"Invalid created_by value: {value} does not exist.")
        return value     
    
    @validates('deleted')
    def validate_deleted(self, key, value):
        if not isinstance(value, YNEnum):
            raise ValueError(f"Invalid deleted value: {value}")
        return value 

    def __init__(self, derived, deleted = YNEnum.NO, created_by=None, updated_by=None,created_date = datetime.now(),updated_date = datetime.now(),**kwargs):
        super().__init__(derived,**kwargs)
        if isinstance(deleted, str):
            self.deleted = YNEnum.NO
        else:
            self.deleted = deleted
        self.created_by = created_by
        self.updated_by = updated_by
        self.created_date = created_date
        self.updated_date = updated_date



class Application(BaseAttributes):
    __tablename__ = 'applications'
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(50), nullable=False)
    index = db.Column(db.String(50))
    api = db.Column(db.String(50))

    def __init__(self, name, description, index=None, api=None,**kwargs):
        super().__init__(self,**kwargs)
        self.name = name
        self.description = description
        self.index = index
        self.api = api

    def __repr__(self):
        return f"<Application(id={self.id}, name={self.name}, description={self.description}, index={self.index})>"

class Account(BaseAttributes):
    __tablename__ = "accounts"
    username = db.Column(db.String(30), unique=True, index=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    verified_by = db.Column(db.Integer, nullable=True)
    verified_date = db.Column(DateTime, server_default=func.now())
    status = db.Column(SQLAEnum(AccountStatusEnum), nullable=False, server_default="INACTIVE")
    user_id = db.Column(db.Integer, nullable=False, index=True)
    wrongAttempt = db.Column(db.Integer, server_default="0")

    @validates('status')
    def validate_status(self, key, value):
        if not isinstance(value, AccountStatusEnum):
            raise ValueError(f"Invalid status value: {value}")
        return value
    
    @validates('verified_by')
    def validate_verified_by(self, key, value):
        if value is not None:
            if value == 0:
                return value
            if not db.session.query(Account.id).filter_by(id=value).first():
                raise ValueError(f"Invalid verified_by value: {value} does not exist.")
        return value

    def __init__(self, username, password, user_id=None, verified_by=None, status=AccountStatusEnum.INACTIVE, wrongAttempt=0,verified_date=func.now(),**kwargs):
        super().__init__(self,**kwargs)
        self.username = username
        if not password:
            self.password = ""
        else:
            self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.verified_by = verified_by
        self.verified_date = verified_date
        if isinstance(status, str):
            self.status = AccountStatusEnum.INACTIVE
        else:
            self.status = status
        self.user_id = user_id
        self.wrongAttempt = wrongAttempt

    def __repr__(self):
        return f'Account(ID: {self.id}, Name: "{self.username}", Password: "{self.password}")'

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def isVerified(self):
        return self.status == AccountStatusEnum.ACTIVE

    def verify(self, verified_by):
        self.status = AccountStatusEnum.ACTIVE
        self.verified_by = verified_by
        self.verified_date = datetime.now()

    def isNotVerified(self):
        return self.status == AccountStatusEnum.INACTIVE

    def isBlocked(self):
        return self.status == AccountStatusEnum.BLOCKED

    def blockAccount(self):
        self.status = AccountStatusEnum.BLOCKED

class Role(BaseAttributes):
    __tablename__ = "roles"
    
    role = db.Column(db.String(30), index=True, nullable=False, unique=True)

    def __init__(self, role,**kwargs):
        super().__init__(self,**kwargs)
        self.role = role.upper()

    def __repr__(self):
        return f'Role({self.id}, "{self.role}")'
    
    @classmethod
    @RouteMeta.route(__tablename__, '/custom', methods=['GET'])
    def custom_route(cls):
        return jsonify({"message": "Custom method response"}), 200