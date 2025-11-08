# routes/ui_config_route.py
from flask import Blueprint, jsonify, request
from models.models import UIScreen, UIComponent, UIAction
from extensions import db


ui_config_bp = Blueprint('ui_config_bp', __name__)

@ui_config_bp.route('/ui/screens', methods=['GET'])
def get_all_screens():
    """Obtener todas las pantallas configuradas"""
    try:
        screens = UIScreen.query.filter_by(estatus=1).order_by(UIScreen.order_index).all()
        return jsonify({
            "success": True,
            "screens": [s.to_dict() for s in screens]
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@ui_config_bp.route('/ui/screens/<screen_name>', methods=['GET'])
def get_screen_config(screen_name):
    """Obtener configuración completa de una pantalla específica"""
    try:
        screen = UIScreen.query.filter_by(screen_name=screen_name, estatus=1).first()
        
        if not screen:
            return jsonify({
                "success": False,
                "message": "Pantalla no encontrada"
            }), 404
        
        return jsonify({
            "success": True,
            "screen": screen.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@ui_config_bp.route('/ui/screens', methods=['POST'])
def create_screen():
    """Crear nueva pantalla (Admin)"""
    try:
        data = request.get_json()
        
        new_screen = UIScreen(
            screen_name=data['screen_name'],
            title=data['title'],
            description=data.get('description'),
            icon=data.get('icon'),
            order_index=data.get('order_index', 0)
        )
        
        db.session.add(new_screen)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Pantalla creada",
            "screen": new_screen.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

@ui_config_bp.route('/ui/components', methods=['POST'])
def create_component():
    """Agregar componente a una pantalla (Admin)"""
    try:
        data = request.get_json()
        
        new_component = UIComponent(
            screen_id=data['screen_id'],
            component_type=data['component_type'],
            component_id=data['component_id'],
            label=data.get('label'),
            placeholder=data.get('placeholder'),
            validation_rules=data.get('validation_rules'),
            properties=data.get('properties'),
            order_index=data.get('order_index', 0),
            is_required=data.get('is_required', 0)
        )
        
        db.session.add(new_component)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Componente creado",
            "component": new_component.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500