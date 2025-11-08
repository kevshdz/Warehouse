from flask import Blueprint, jsonify, request
from models.models import Producto
from extensions import db


shoes_bp = Blueprint('shoes_bp', __name__)

@shoes_bp.route('/shoes', methods=['POST'])
def createShoe():
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
        
        # Generar el id_producto automáticamente (ejemplo: ZAP001, ZAP002, etc.)
        ultimo_producto = Producto.query.filter(
            Producto.id_producto.like('ZAP%')
        ).order_by(Producto.id_producto.desc()).first()
        
        if ultimo_producto:
            # Extraer el número del último id y incrementar
            ultimo_numero = int(ultimo_producto.id_producto.replace('ZAP', ''))
            nuevo_numero = ultimo_numero + 1
        else:
            nuevo_numero = 1
        
        nuevo_id_producto = f'ZAP{nuevo_numero:03d}'  # Formato: ZAP001, ZAP002...
        
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
            "message": "Zapato creado exitosamente",
            "producto": nuevo_producto.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error al crear el zapato: {str(e)}"
        }), 500

@shoes_bp.route('/shoes', methods=['GET'])
def getShoes():
    # Obtener parámetro de query para filtrar por estatus
    estatus = request.args.get('estatus', None)
    
    query = Producto.query.filter(Producto.id_producto.like('%ZAP%'))
    
    # Filtrar por estatus si se proporciona
    if estatus is not None:
        query = query.filter(Producto.estatus == int(estatus))
    
    productos = query.all()
    data = [p.to_dict() for p in productos]
    
    return jsonify({
        "success": True,
        "total": len(data),
        "productos": data
    })

@shoes_bp.route('/shoes/<int:id>', methods=['PUT'])
def editShoes(id):
    try:
        # Buscar el producto por ID
        producto = Producto.query.get(id)
        
        if not producto:
            return jsonify({
                "success": False,
                "message": "Zapato no encontrado"
            }), 404
        
        # Verificar que sea un zapato (que tenga ZAP en el id_producto)
        if not producto.id_producto.startswith('ZAP'):
            return jsonify({
                "success": False,
                "message": "Este producto no es un zapato"
            }), 400
        
        # Obtener datos del request
        data = request.get_json()
        
        # Actualizar solo los campos que se envíen
        if 'nombre' in data:
            producto.nombre = data['nombre']
        
        if 'descripcion' in data:
            producto.descripcion = data['descripcion']
        
        if 'imagen' in data:
            producto.imagen = data['imagen']
        
        if 'cantidad' in data:
            producto.cantidad = data['cantidad']
        
        if 'estatus' in data:
            producto.estatus = data['estatus']
        
        if 'idUsuario' in data:
            producto.idUsuario = data['idUsuario']
        
        # Guardar cambios
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Zapato actualizado exitosamente",
            "producto": producto.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error al actualizar el zapato: {str(e)}"
        }), 500

@shoes_bp.route('/shoes/<int:id>', methods=['DELETE'])
def deleteShoes(id):
    try:
        # Buscar el producto por ID
        producto = Producto.query.get(id)
        
        if not producto:
            return jsonify({
                "success": False,
                "message": "Zapato no encontrado"
            }), 404
        
        # Verificar que sea un zapato
        if not producto.id_producto.startswith('ZAP'):
            return jsonify({
                "success": False,
                "message": "Este producto no es un zapato"
            }), 400
        
        # Verificar si ya está inactivo
        if producto.estatus == 0:
            return jsonify({
                "success": False,
                "message": "El zapato ya está inactivo"
            }), 400
        
        # Cambiar estatus a 0 (inactivo) en lugar de eliminar
        producto.estatus = 0
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Zapato desactivado exitosamente",
            "producto": producto.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error al desactivar el zapato: {str(e)}"
        }), 500

@shoes_bp.route('/shoes/search', methods=['GET'])
def searchShoes():
    try:
        # Obtener parámetros de búsqueda
        id_producto = request.args.get('id_producto', None)
        nombre = request.args.get('nombre', None)
        estatus = request.args.get('estatus', None)
        
        # Construir query base
        query = Producto.query.filter(Producto.id_producto.like('%ZAP%'))
        
        # Aplicar filtros dinámicamente
        if id_producto:
            query = query.filter(Producto.id_producto == id_producto)
        
        if nombre:
            # Búsqueda parcial case-insensitive
            query = query.filter(Producto.nombre.ilike(f'%{nombre}%'))
        
        if estatus is not None:
            query = query.filter(Producto.estatus == int(estatus))
        
        # Ejecutar query
        productos = query.all()
        
        if not productos:
            return jsonify({
                "success": False,
                "message": "No se encontraron zapatos con los criterios especificados",
                "total": 0,
                "productos": []
            }), 404
        
        data = [p.to_dict() for p in productos]
        
        return jsonify({
            "success": True,
            "total": len(data),
            "productos": data
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error en la búsqueda: {str(e)}"
        }), 500
