from flask import Flask
from extensions import db
from routes.shoes_route import shoes_bp
from routes.screen_config_route import ui_config_bp
from routes.jacket_routes import jackets_bp
from routes.pants_route import pants_bp
from routes.accesories_route import accessories_bp
from routes.shirts_route import shirts_bp
from routes.sport_wear import sportswear_bp
from routes.auth_routes import auth_bp




def create_app():
    app = Flask(__name__)

    # Configuración de la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/warehouse_personal'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar SQLAlchemy
    db.init_app(app)

    # Registrar rutas (blueprints)
    app.register_blueprint(shoes_bp)
    app.register_blueprint(ui_config_bp)
    app.register_blueprint(jackets_bp)
    app.register_blueprint(pants_bp)
    app.register_blueprint(accessories_bp)
    app.register_blueprint(shirts_bp)
    app.register_blueprint(sportswear_bp)
    app.register_blueprint(auth_bp)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)