from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


"""
class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_producto = db.Column(db.String(50), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    imagen = db.Column(db.String(255))
    cantidad = db.Column(db.Integer, default=0)
    estatus = db.Column(db.SmallInteger, default=1)  # 1 = activo, 0 = inactivo
    idUsuario = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "id_producto": self.id_producto,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "imagen": self.imagen,
            "cantidad": self.cantidad,
            "estatus": self.estatus,
            "idUsuario": self.idUsuario,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
"""

# models/models.py
from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

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
    
    productos = db.relationship('Producto', backref='usuario', lazy=True)
    
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


class Producto(db.Model):
    __tablename__ = 'productos'
    
    id = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.String(50), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    imagen = db.Column(db.String(255))
    cantidad = db.Column(db.Integer, default=0)
    estatus = db.Column(db.Integer, default=1)
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_producto': self.id_producto,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'imagen': self.imagen,
            'cantidad': self.cantidad,
            'estatus': self.estatus,
            'idUsuario': self.idUsuario,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class UIScreen(db.Model):
    __tablename__ = 'ui_screens'
    
    id = db.Column(db.Integer, primary_key=True)
    screen_name = db.Column(db.String(100), unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    order_index = db.Column(db.Integer, default=0)
    estatus = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    components = db.relationship('UIComponent', backref='screen', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'screen_name': self.screen_name,
            'title': self.title,
            'description': self.description,
            'icon': self.icon,
            'order_index': self.order_index,
            'estatus': self.estatus,
            'components': [c.to_dict() for c in sorted(self.components, key=lambda x: x.order_index)]
        }


class UIComponent(db.Model):
    __tablename__ = 'ui_components'
    
    id = db.Column(db.Integer, primary_key=True)
    screen_id = db.Column(db.Integer, db.ForeignKey('ui_screens.id'), nullable=False)
    component_type = db.Column(db.String(50), nullable=False)
    component_id = db.Column(db.String(100), nullable=False)
    label = db.Column(db.String(255))
    placeholder = db.Column(db.String(255))
    validation_rules = db.Column(db.JSON)
    properties = db.Column(db.JSON)
    order_index = db.Column(db.Integer, default=0)
    is_required = db.Column(db.Integer, default=0)
    estatus = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    actions = db.relationship('UIAction', backref='component', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'component_type': self.component_type,
            'component_id': self.component_id,
            'label': self.label,
            'placeholder': self.placeholder,
            'validation_rules': self.validation_rules,
            'properties': self.properties,
            'order_index': self.order_index,
            'is_required': bool(self.is_required),
            'actions': [a.to_dict() for a in self.actions]
        }

class UIAction(db.Model):
    __tablename__ = 'ui_actions'
    
    id = db.Column(db.Integer, primary_key=True)
    component_id = db.Column(db.Integer, db.ForeignKey('ui_components.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)
    endpoint = db.Column(db.String(255))
    http_method = db.Column(db.String(10), default='GET')
    params = db.Column(db.JSON)
    navigation_target = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'action_type': self.action_type,
            'endpoint': self.endpoint,
            'http_method': self.http_method,
            'params': self.params,
            'navigation_target': self.navigation_target
        }