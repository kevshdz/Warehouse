from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json


class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(20))
    fecha_nacimiento = db.Column(db.Date)
    rol = db.Column(db.String(20), default='user')
    estatus = db.Column(db.Integer, default=1)
    email_verificado = db.Column(db.Integer, default=0)
    ultimo_acceso = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    
    def set_password(self, password):
        """
        Hashear la contraseña usando pbkdf2:sha256
        Compatible con todas las versiones de Python
        """
        self.password_hash = generate_password_hash(
            password, 
            method='pbkdf2:sha256',  # ✅ Método compatible
            salt_length=16
        )
    
    def check_password(self, password):
        """Verificar la contraseña"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_sensitive=False):
        """Convertir a diccionario (sin datos sensibles por defecto)"""
        data = {
            'id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'email': self.email,
            'telefono': self.telefono,
            'fecha_nacimiento': self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            'rol': self.rol,
            'estatus': self.estatus,
            'email_verificado': bool(self.email_verificado),
            'ultimo_acceso': self.ultimo_acceso.isoformat() if self.ultimo_acceso else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
        
        return data

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
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = db.Column(db.SmallInteger, default=1)
    
    category = db.relationship('Category', backref='submissions')
    values = db.relationship('FormValue', backref='submission', lazy=True)
    
    def to_dict(self, include_values=False):
        data = {
            'id': self.id,
            'category_id': self.category_id,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
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