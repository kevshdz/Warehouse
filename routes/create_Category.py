from flask import Blueprint, jsonify, request, send_from_directory, current_app
from models.models import *
from extensions import db
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from decimal import Decimal
import json

categories_bp = Blueprint('categories_bp', __name__)

@categories_bp.route('/create/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    category = Category(
        name=data['name'],
        description=data.get('description'),
        active=data.get('active', 1)
    )
    
    db.session.add(category)
    db.session.commit()
    
    return jsonify(category.to_dict()), 201


@categories_bp.route('/create/category-fields', methods=['POST'])
def create_fields_bulk():
    data = request.get_json()
    
    fields = []
    for item in data['fields']:
        field = CategoryField(
            category_id=item['category_id'],
            name=item['name'],
            field_type=item['field_type'],
            required=item.get('required', 0),
            active=item.get('active', 1)
        )
        db.session.add(field)
        fields.append(field)
    
    db.session.commit()
    
    return jsonify([f.to_dict() for f in fields]), 201

@categories_bp.route('/field-options', methods=['POST'])
def create_field_options():
    data = request.get_json()
    
    options = []
    for item in data['options']:
        option = FieldOption(
            field_id=item['field_id'],
            value=item['value'],
            active=item.get('active', 1)
        )
        db.session.add(option)
        options.append(option)
    
    db.session.commit()
    
    return jsonify([opt.to_dict() for opt in options]), 201