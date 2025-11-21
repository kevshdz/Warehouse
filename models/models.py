from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.SmallInteger, default=1)
    
    fields = db.relationship('CategoryField', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    def to_dict(self, include_fields=False):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'active': self.active
        }
        if include_fields:
            data['fields'] = [field.to_dict() for field in self.fields]
        return data


class CategoryField(db.Model):
    __tablename__ = 'category_fields'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    field_type = db.Column(db.String(50), nullable=False)
    required = db.Column(db.SmallInteger, default=0)
    active = db.Column(db.SmallInteger, default=1)
    
    options = db.relationship('FieldOption', backref='field', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'name': self.name,
            'field_type': self.field_type,
            'required': self.required,
            'active': self.active,
            'options': [opt.to_dict() for opt in self.options] if self.field_type == 'select' else None
        }

class FieldOption(db.Model):
    __tablename__ = 'field_options'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    field_id = db.Column(db.Integer, db.ForeignKey('category_fields.id'), nullable=False)
    value = db.Column(db.String(100), nullable=False)
    active = db.Column(db.SmallInteger, default=1)
    
    def to_dict(self):
        return {
            'id': self.id,
            'field_id': self.field_id,
            'value': self.value,
            'active': self.active
        }

class FormSubmission(db.Model):
    __tablename__ = 'form_submissions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = db.Column(db.SmallInteger, default=1)
    
    category = db.relationship('Category', backref='submissions')
    values = db.relationship('FormValue', backref='submission', lazy=True)
    
    def to_dict(self, include_values=False):
        data = {
            'id': self.id,
            'category_id': self.category_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'active': self.active
        }
        if include_values:
            data['values'] = [val.to_dict() for val in self.values]
        return data


class FormValue(db.Model):
    __tablename__ = 'form_values'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('form_submissions.id'), nullable=False)
    field_id = db.Column(db.Integer, db.ForeignKey('category_fields.id'), nullable=False)
    value = db.Column(db.Text, nullable=True)
    
    field = db.relationship('CategoryField')
    
    def to_dict(self):
        return {
            'id': self.id,
            'field_id': self.field_id,
            'field_name': self.field.name,
            'field_type': self.field.field_type,
            'value': self.value
        }