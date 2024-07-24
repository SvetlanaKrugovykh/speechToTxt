# app.py
from dotenv import load_dotenv
from flask import Flask
import os

load_dotenv('env')

def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))

    with app.app_context():
        from .routes import main as main_blueprint
        app.register_blueprint(main_blueprint)

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv('PORT', '8338'))
    cert_path = os.getenv('CERT_PATH')
    key_path = os.getenv('KEY_PATH')
    test_cert_path_exist =  os.path.exists(cert_path)
    test_key_path_exist = os.path.exists(key_path)
    
    print(f"Starting server on port {port}")
    print(f"SSL certificates found: {test_cert_path_exist and test_key_path_exist}")
    
    if cert_path and key_path:
        app.run(ssl_context=(cert_path, key_path), host='0.0.0.0', port=port, debug=False)
    else:
        print("Error: SSL certificates not found or paths not set.")
        app.run(host='0.0.0.0', port=port, debug=False)
