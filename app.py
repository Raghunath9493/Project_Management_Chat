import os
from flask import Flask, jsonify, session
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from routes.routes import register_routes

def create_app():
    app = Flask(__name__)

    # Load configuration
    config_name = os.getenv('FLASK_CONFIG', 'DevelopmentConfig')
    app.config.from_object(f'config.{config_name}')

    CORS(app)
    bcrypt = Bcrypt(app)
    jwt = JWTManager(app)

    # Import and register routes
    register_routes(app)

    @app.errorhandler(Exception)
    def handle_error(error):
        message = str(error)
        code = 500  # Internal Server Error

        # Handle specific exceptions and set appropriate error codes
        if isinstance(error, KeyError):
            message = "Missing required data"
            code = 400  # Bad Request

        return jsonify({"error": message}), code

    return app

# Run the app if called directly
if __name__ == '__main__':
    app = create_app()
    app.run(port=5500,debug=True)