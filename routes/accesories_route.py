from flask import Blueprint, jsonify, request, send_from_directory, current_app
from models.models import Producto
from extensions import db
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from decimal import Decimal
import json

accessories_bp = Blueprint('accessories_bp', __name__)

UPLOAD_FOLDER = 'img/accesories'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  
MIN_IMAGES = 1  
MAX_IMAGES = 5  

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_unique_filename(filename):
    name, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    clean_name = secure_filename(name)
    return f"{clean_name}_{timestamp}{ext}"


@accessories_bp.route('/img/accesories/<filename>', methods=['GET'])
def serve_image(filename):
    """Servir imágenes desde img/accesories"""
    try:
        upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
        return send_from_directory(upload_path, filename)
    except FileNotFoundError:
        return jsonify({
            "success": False,
            "message": f"Imagen '{filename}' no encontrada"
        }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500


@accessories_bp.route('/accessories', methods=['POST'])
def createAccessory():
    try:
        if request.content_type and 'multipart/form-data' in request.content_type:
            nombre = request.form.get('nombre')
            descripcion = request.form.get('descripcion')
            cantidad = request.form.get('cantidad')
            precio = request.form.get('precio')
            idUsuario = request.form.get('idUsuario')
            estatus = request.form.get('estatus', 1)
            
            print("Form data:", dict(request.form))
            print("Files recibidos:", request.files)
            print("Keys de files:", list(request.files.keys()))
            
            if not all([nombre, descripcion, cantidad, precio, idUsuario]):
                return jsonify({
                    "success": False,
                    "message": "Todos los campos son requeridos (nombre, descripcion, cantidad, precio, idUsuario)"
                }), 400
        
            try:
                precio_decimal = Decimal(precio)
                if precio_decimal < 0:
                    return jsonify({
                        "success": False,
                        "message": "El precio no puede ser negativo"
                    }), 400
            except (ValueError, TypeError):
                return jsonify({
                    "success": False,
                    "message": "El precio debe ser un número válido"
                }), 400
            
            imagenes_urls = []
            
            files = []
            
            if 'imagenes' in request.files:
                files = request.files.getlist('imagenes')
            elif 'imagenes[]' in request.files:
                files = request.files.getlist('imagenes[]')
                print(f"Encontradas {len(files)} imágenes con key 'imagenes[]'")
            
            elif 'imagen' in request.files:
                files = request.files.getlist('imagen')
                print(f"Encontradas {len(files)} imágenes con key 'imagen'")
            
            else:
                for key in request.files.keys():
                    if 'imagen' in key.lower():
                        files = request.files.getlist(key)
                        print(f"Encontradas {len(files)} imágenes con key '{key}'")
                        break
            
            print(f"Total de archivos detectados: {len(files)}")
            
            if len(files) < MIN_IMAGES:
                return jsonify({
                    "success": False,
                    "message": f"Debes subir al menos {MIN_IMAGES} imagen(es). Enviaste: {len(files)}",
                    "debug": {
                        "files_keys": list(request.files.keys()),
                        "files_count": len(files)
                    }
                }), 400
            
            if len(files) > MAX_IMAGES:
                return jsonify({
                    "success": False,
                    "message": f"Máximo {MAX_IMAGES} imágenes permitidas. Enviaste: {len(files)}"
                }), 400
            
            for idx, file in enumerate(files, 1):
                print(f"\nProcesando imagen {idx}/{len(files)}")
                print(f"   Nombre: {file.filename}")
                
                if file and file.filename != '':
                    if not allowed_file(file.filename):
                        return jsonify({
                            "success": False,
                            "message": f"Extensión no permitida en '{file.filename}'. Solo: {', '.join(ALLOWED_EXTENSIONS)}"
                        }), 400
                    
                    file.seek(0, os.SEEK_END)
                    file_size = file.tell()
                    file.seek(0)
                    
                    print(f"Tamaño: {file_size / 1024:.2f} KB")
                    
                    if file_size > MAX_FILE_SIZE:
                        return jsonify({
                            "success": False,
                            "message": f"El archivo '{file.filename}' es muy grande ({file_size / (1024*1024):.2f}MB). Máximo: 5MB"
                        }), 400
                    
                    upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
                    os.makedirs(upload_path, exist_ok=True)
                    
                    unique_filename = get_unique_filename(file.filename)
                    filepath = os.path.join(upload_path, unique_filename)
                    file.save(filepath)
                    
                    print(f"Guardada en: {filepath}")
                    imagenes_urls.append(f"/img/accesories/{unique_filename}")
            
            if not imagenes_urls:
                return jsonify({
                    "success": False,
                    "message": f"No se pudieron procesar las imágenes. Revisa que sean archivos válidos.",
                    "debug": {
                        "files_received": len(files),
                        "valid_images": len(imagenes_urls)
                    }
                }), 400
            
            print(f"\nTotal de imágenes guardadas: {len(imagenes_urls)}")
            
        else:
            data = request.get_json()
            
            campos_requeridos = ['nombre', 'descripcion', 'imagenes', 'cantidad', 'precio', 'idUsuario']
            for campo in campos_requeridos:
                if campo not in data:
                    return jsonify({
                        "success": False,
                        "message": f"El campo '{campo}' es requerido"
                    }), 400
            
            nombre = data['nombre']
            descripcion = data['descripcion']
            imagenes_urls = data['imagenes']
            cantidad = data['cantidad']
            precio = data['precio']
            idUsuario = data['idUsuario']
            estatus = data.get('estatus', 1)
            
            if not isinstance(imagenes_urls, list):
                return jsonify({
                    "success": False,
                    "message": "'imagenes' debe ser un array de URLs"
                }), 400
            
            if len(imagenes_urls) < MIN_IMAGES or len(imagenes_urls) > MAX_IMAGES:
                return jsonify({
                    "success": False,
                    "message": f"Debes proporcionar entre {MIN_IMAGES} y {MAX_IMAGES} imágenes"
                }), 400
            
            try:
                precio_decimal = Decimal(str(precio))
                if precio_decimal < 0:
                    return jsonify({
                        "success": False,
                        "message": "El precio no puede ser negativo"
                    }), 400
            except (ValueError, TypeError):
                return jsonify({
                    "success": False,
                    "message": "El precio debe ser un número válido"
                }), 400
        
        ultimo_producto = Producto.query.filter(
            Producto.id_producto.like('ACC%')
        ).order_by(Producto.id_producto.desc()).first()
        
        if ultimo_producto:
            ultimo_numero = int(ultimo_producto.id_producto.replace('ACC', ''))
            nuevo_numero = ultimo_numero + 1
        else:
            nuevo_numero = 1
        
        nuevo_id_producto = f'ACC{nuevo_numero:03d}'
        
        nuevo_producto = Producto(
            id_producto=nuevo_id_producto,
            nombre=nombre,
            descripcion=descripcion,
            imagen=json.dumps(imagenes_urls),
            cantidad=int(cantidad),
            precio=Decimal(str(precio)),
            estatus=int(estatus),
            idUsuario=int(idUsuario)
        )
        
        db.session.add(nuevo_producto)
        db.session.commit()
        
        print(f"\n🎉 Producto creado exitosamente: {nuevo_id_producto}")
        
        return jsonify({
            "success": True,
            "message": "Accesorio creado exitosamente",
            "producto": nuevo_producto.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Error al crear el accesorio: {str(e)}"
        }), 500
# ==================== UPDATE ACCESORIO ====================
@accessories_bp.route('/accessories/<int:id>', methods=['PUT'])
def editAccessory(id):
    try:
        producto = Producto.query.get(id)
        
        if not producto:
            return jsonify({
                "success": False,
                "message": "Accesorio no encontrado"
            }), 404
        
        if not producto.id_producto.startswith('ACC'):
            return jsonify({
                "success": False,
                "message": "Este producto no es un accesorio"
            }), 400
        
        if request.content_type and 'multipart/form-data' in request.content_type:
            if 'nombre' in request.form:
                producto.nombre = request.form.get('nombre')
            if 'descripcion' in request.form:
                producto.descripcion = request.form.get('descripcion')
            if 'cantidad' in request.form:
                producto.cantidad = int(request.form.get('cantidad'))
            if 'precio' in request.form:
                producto.precio = Decimal(request.form.get('precio'))
            if 'estatus' in request.form:
                producto.estatus = int(request.form.get('estatus'))
            
            if 'imagenes' in request.files:
                files = request.files.getlist('imagenes')
                
                if len(files) > MAX_IMAGES:
                    return jsonify({
                        "success": False,
                        "message": f"Máximo {MAX_IMAGES} imágenes"
                    }), 400
                
                try:
                    old_images = json.loads(producto.imagen) if producto.imagen else []
                    for old_img in old_images:
                        if old_img.startswith('/img/accesories/'):
                            old_filename = old_img.split('/')[-1]
                            old_filepath = os.path.join(
                                current_app.root_path,
                                UPLOAD_FOLDER,
                                old_filename
                            )
                            if os.path.exists(old_filepath):
                                os.remove(old_filepath)
                                print(f"🗑️ Imagen antigua eliminada: {old_filename}")
                except Exception as e:
                    print(f"Error eliminando imágenes antiguas: {e}")
                
                nuevas_imagenes = []
                upload_path = os.path.join(current_app.root_path, UPLOAD_FOLDER)
                
                for file in files:
                    if file and file.filename != '':
                        if not allowed_file(file.filename):
                            continue
                        
                        unique_filename = get_unique_filename(file.filename)
                        filepath = os.path.join(upload_path, unique_filename)
                        file.save(filepath)
                        nuevas_imagenes.append(f"/img/accesories/{unique_filename}")
                
                if nuevas_imagenes:
                    producto.imagen = json.dumps(nuevas_imagenes)
        else:
            data = request.get_json()
            
            if 'nombre' in data:
                producto.nombre = data['nombre']
            if 'descripcion' in data:
                producto.descripcion = data['descripcion']
            if 'imagenes' in data:
                if isinstance(data['imagenes'], list):
                    producto.imagen = json.dumps(data['imagenes'])
            if 'cantidad' in data:
                producto.cantidad = data['cantidad']
            if 'precio' in data:
                producto.precio = Decimal(str(data['precio']))
            if 'estatus' in data:
                producto.estatus = data['estatus']
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Accesorio actualizado exitosamente",
            "producto": producto.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error al actualizar el accesorio: {str(e)}"
        }), 500


@accessories_bp.route('/accessories', methods=['GET'])
def getAccessories():
    try:
        estatus = request.args.get('estatus', None)
        query = Producto.query.filter(Producto.id_producto.like('%ACC%'))
        
        if estatus is not None:
            query = query.filter(Producto.estatus == int(estatus))
        
        productos = query.all()
        data = [p.to_dict() for p in productos]
        
        return jsonify({
            "success": True,
            "total": len(data),
            "productos": data
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500


@accessories_bp.route('/accessories/<int:id>', methods=['DELETE'])
def deleteAccessory(id):
    try:
        producto = Producto.query.get(id)
        
        if not producto:
            return jsonify({
                "success": False,
                "message": "Accesorio no encontrado"
            }), 404
        
        if not producto.id_producto.startswith('ACC'):
            return jsonify({
                "success": False,
                "message": "Este producto no es un accesorio"
            }), 400
        
        if producto.estatus == 0:
            return jsonify({
                "success": False,
                "message": "El accesorio ya está inactivo"
            }), 400
        
        try:
            imagenes = json.loads(producto.imagen) if producto.imagen else []
            for img_url in imagenes:
                if img_url.startswith('/img/accesories/'):
                    filename = img_url.split('/')[-1]
                    filepath = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        print(f"🗑️ Imagen eliminada: {filename}")
        except Exception as e:
            print(f"Error eliminando imágenes: {e}")
        
        producto.estatus = 0
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Accesorio desactivado exitosamente",
            "producto": producto.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error al desactivar el accesorio: {str(e)}"
        }), 500