from flask import Blueprint, request, jsonify
from models.models import FormSubmission, FormValue, CategoryField
from extensions import db
import os
import uuid


forms_bp = Blueprint('forms', __name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(file):
    if file and allowed_file(file.filename):
        # Genera nombre único para evitar duplicados
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        
        # Crea la carpeta si no existe
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Guarda el archivo
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Retorna la URL
        return f"/static/uploads/{filename}"
    return None


@forms_bp.route('/submissions', methods=['POST'])
def create_submission():
    # Obtener category_id del form
    category_id = request.form.get('category_id')
    
    # Crear el submission
    submission = FormSubmission(category_id=category_id)
    db.session.add(submission)
    db.session.flush()
    
    # Obtener los campos de esta categoría
    fields = CategoryField.query.filter_by(category_id=category_id).all()
    
    for field in fields:
        value = None
        
        if field.field_type == 'image':
            # Buscar archivo con el nombre del campo
            file = request.files.get(f'field_{field.id}')
            if file:
                value = save_image(file)
        else:
            # Campos normales (text, number, date, etc.)
            value = request.form.get(f'field_{field.id}')
        
        form_value = FormValue(
            submission_id=submission.id,
            field_id=field.id,
            value=value
        )
        db.session.add(form_value)
    
    db.session.commit()
    
    return jsonify(submission.to_dict(include_values=True)), 201