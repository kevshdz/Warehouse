from flask import Blueprint, jsonify, request
from models.models import Producto
from extensions import db

sportswear_bp = Blueprint('sportswear_bp', __name__)

@sportswear_bp.route('/sportswear', methods=['POST'])
def createSportswear():
    try:
        # Obtener datos del request
        data = request.get_json()
        
        # Validar campos requeridos
        campos_requeridos = ['nombre', 'descripcion', 'imagen', 'cantidad', 'idUsuario']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({
                    "success": False,
                    "message": f"El campo '{campo}' es requerido"
                }), 400
        
        # Generar el id_producto automáticamente (ejemplo: DEP001, DEP002, etc.)
        ultimo_producto = Producto.query.filter(
            Producto.id_producto.like('DEP%')
        ).order_by(Producto.id_producto.desc()).first()
        
        if ultimo_producto:
            # Extraer el número del último id y incrementar
            ultimo_numero = int(ultimo_producto.id_producto.replace('DEP', ''))
            nuevo_numero = ultimo_numero + 1
        else:
            nuevo_numero = 1
        
        nuevo_id_producto = f'DEP{nuevo_numero:03d}'  # Formato: DEP001, DEP002...
        
        # Crear nuevo producto
        nuevo_producto = Producto(
            id_producto=nuevo_id_producto,
            nombre=data['nombre'],
            descripcion=data['descripcion'],
            imagen=data['imagen'],
            cantidad=data['cantidad'],
            estatus=data.get('estatus', 1),  # Por defecto 1 (activo)
            idUsuario=data['idUsuario']
        )
        
        # Guardar en la base de datos
        db.session.add(nuevo_producto)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Ropa deportiva creada exitosamente",
            "producto": nuevo_producto.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error al crear la ropa deportiva: {str(e)}"
        }), 500
