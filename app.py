from flask import Flask
from extensions import db
from routes.create_Category import categories_bp
from routes.create_forms import forms_bp





def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/warehouse_personal'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    app.register_blueprint(categories_bp)
    app.register_blueprint(forms_bp)
    

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)