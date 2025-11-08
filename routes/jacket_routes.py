from flask import Blueprint, jsonify, request
from models.models import Producto
from extensions import db

jackets_bp = Blueprint('jackets_bp', __name__)

@jackets_bp.route('/jackets', methods=['POST'])
def createJacket():
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
        
        # Generar el id_producto automáticamente (ejemplo: CHA001, CHA002, etc.)
        ultimo_producto = Producto.query.filter(
            Producto.id_producto.like('CHA%')
        ).order_by(Producto.id_producto.desc()).first()
        
        if ultimo_producto:
            # Extraer el número del último id y incrementar
            ultimo_numero = int(ultimo_producto.id_producto.replace('CHA', ''))
            nuevo_numero = ultimo_numero + 1
        else:
            nuevo_numero = 1
        
        nuevo_id_producto = f'CHA{nuevo_numero:03d}'  # Formato: CHA001, CHA002...
        
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
            "message": "Chamarra creada exitosamente",
            "producto": nuevo_producto.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error al crear la chamarra: {str(e)}"
        }), 500

