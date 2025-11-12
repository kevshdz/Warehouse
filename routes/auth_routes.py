# routes/auth_route.py
from flask import Blueprint, jsonify, request
from models.models import Usuario
from extensions import db
from datetime import datetime
import re

auth_bp = Blueprint('auth_bp', __name__)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$')

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        campos_requeridos = ['nombre', 'apellido', 'email', 'password']
        for campo in campos_requeridos:
            if campo not in data or not data[campo]:
                return jsonify({
                    "success": False,
                    "message": f"El campo '{campo}' es requerido"
                }), 400
        
        if not EMAIL_REGEX.match(data['email']):
            return jsonify({
                "success": False,
                "message": "Formato de email inválido"
            }), 400
        
        if not PASSWORD_REGEX.match(data['password']):
            return jsonify({
                "success": False,
                "message": "La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula y un número"
            }), 400
        
        usuario_existente = Usuario.query.filter_by(email=data['email'].lower()).first()
        if usuario_existente:
            return jsonify({
                "success": False,
                "message": "El email ya está registrado"
            }), 409
        
        nuevo_usuario = Usuario(
            nombre=data['nombre'].strip(),
            apellido=data['apellido'].strip(),
            email=data['email'].lower().strip(),
            telefono=data.get('telefono'),
            fecha_nacimiento=data.get('fecha_nacimiento'),
            rol=data.get('rol', 'user')
        )
        
        nuevo_usuario.set_password(data['password'])
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Usuario registrado exitosamente",
            "usuario": nuevo_usuario.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error al registrar usuario: {str(e)}"
        }), 500


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({
                "success": False,
                "message": "Email y contraseña son requeridos"
            }), 400
        
        usuario = Usuario.query.filter_by(email=data['email'].lower().strip()).first()
        
        if not usuario or not usuario.check_password(data['password']):
            return jsonify({
                "success": False,
                "message": "Credenciales inválidas"
            }), 401
        
        if usuario.estatus == 0:
            return jsonify({
                "success": False,
                "message": "Usuario inactivo. Contacta al administrador"
            }), 403
        
        usuario.ultimo_acceso = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Login exitoso",
            "usuario": usuario.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error en el login: {str(e)}"
        }), 500

@auth_bp.route('/auth/profile/<int:id>', methods=['GET'])
def get_profile(id):
    try:
        usuario = Usuario.query.get(id)
        
        if not usuario:
            return jsonify({
                "success": False,
                "message": "Usuario no encontrado"
            }), 404
        
        return jsonify({
            "success": True,
            "usuario": usuario.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500


@auth_bp.route('/auth/profile/<int:id>', methods=['PUT'])
def update_profile(id):
    try:
        usuario = Usuario.query.get(id)
        
        if not usuario:
            return jsonify({
                "success": False,
                "message": "Usuario no encontrado"
            }), 404
        
        data = request.get_json()
        
        if 'nombre' in data:
            usuario.nombre = data['nombre'].strip()
        
        if 'apellido' in data:
            usuario.apellido = data['apellido'].strip()
        
        if 'telefono' in data:
            usuario.telefono = data['telefono']
        
        if 'fecha_nacimiento' in data:
            usuario.fecha_nacimiento = data['fecha_nacimiento']
        
        if 'email' in data:
            if not EMAIL_REGEX.match(data['email']):
                return jsonify({
                    "success": False,
                    "message": "Formato de email inválido"
                }), 400
            
            email_existente = Usuario.query.filter(
                Usuario.email == data['email'].lower(),
                Usuario.id != id
            ).first()
            
            if email_existente:
                return jsonify({
                    "success": False,
                    "message": "El email ya está en uso"
                }), 409
            
            usuario.email = data['email'].lower().strip()
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Perfil actualizado exitosamente",
            "usuario": usuario.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error al actualizar perfil: {str(e)}"
        }), 500


@auth_bp.route('/auth/change-password/<int:id>', methods=['POST'])
def change_password(id):
    try:
        usuario = Usuario.query.get(id)
        
        if not usuario:
            return jsonify({
                "success": False,
                "message": "Usuario no encontrado"
            }), 404
        
        data = request.get_json()
        
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({
                "success": False,
                "message": "Contraseña actual y nueva son requeridas"
            }), 400
        
        if not usuario.check_password(data['current_password']):
            return jsonify({
                "success": False,
                "message": "Contraseña actual incorrecta"
            }), 401
        
        if not PASSWORD_REGEX.match(data['new_password']):
            return jsonify({
                "success": False,
                "message": "La nueva contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula y un número"
            }), 400
        
        usuario.set_password(data['new_password'])
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Contraseña actualizada exitosamente"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error al cambiar contraseña: {str(e)}"
        }), 500


@auth_bp.route('/auth/users', methods=['GET'])
def list_users():
    try:
        estatus = request.args.get('estatus', None)
        rol = request.args.get('rol', None)
        
        query = Usuario.query
        
        if estatus is not None:
            query = query.filter(Usuario.estatus == int(estatus))
        
        if rol:
            query = query.filter(Usuario.rol == rol)
        
        usuarios = query.all()
        data = [u.to_dict() for u in usuarios]
        
        return jsonify({
            "success": True,
            "total": len(data),
            "usuarios": data
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500


@auth_bp.route('/auth/users/<int:id>/deactivate', methods=['PATCH'])
def deactivate_user(id):
    try:
        usuario = Usuario.query.get(id)
        
        if not usuario:
            return jsonify({
                "success": False,
                "message": "Usuario no encontrado"
            }), 404
        
        if usuario.estatus == 0:
            return jsonify({
                "success": False,
                "message": "El usuario ya está inactivo"
            }), 400
        
        usuario.estatus = 0
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Usuario desactivado exitosamente",
            "usuario": usuario.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500


@auth_bp.route('/auth/users/<int:id>/activate', methods=['PATCH'])
def activate_user(id):
    try:
        usuario = Usuario.query.get(id)
        
        if not usuario:
            return jsonify({
                "success": False,
                "message": "Usuario no encontrado"
            }), 404
        
        if usuario.estatus == 1:
            return jsonify({
                "success": False,
                "message": "El usuario ya está activo"
            }), 400
        
        usuario.estatus = 1
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Usuario reactivado exitosamente",
            "usuario": usuario.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500