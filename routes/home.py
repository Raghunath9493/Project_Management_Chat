from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask import current_app as app
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from mongoengine.errors import DoesNotExist
from models import User

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    data = request.form
    username = data.get('username')
    password = data.get('password')

    try:
        user = User.objects.get(username=username)
    except DoesNotExist:
        return jsonify({"msg": "User not found"}), 404

    if bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Invalid credentials"}), 401
