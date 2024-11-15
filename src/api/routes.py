"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User
from api.utils import generate_sitemap, APIException
from flask_cors import CORS

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api)


@api.route('/user', methods=['GET'])
def get_user():

    all_users = User.query.all()
    results = list(map(lambda usuario: usuario.serialize() ,all_users))
    

    return jsonify(results), 200

@api.route('/user', methods=['POST'])
def add_user():

    body = request.get_json()
    new_user= User(
        email= body['email'],
        password= body['password'],
        is_active=True
    )

    db.session.add(new_user)
    db.session.commit()
    
    all_users = User.query.all()
    results = list(map(lambda usuario: usuario.serialize() ,all_users))
    

    return jsonify(results), 200

@api.route('/login', methods=['POST'])
def login():
    email = request.json.get("email",None)
    password = request.json.get("password",None)
    
    user = User.query.filter_by(email=email).first()

    if user == None:
        return jsonify({"msg":"Could not find email"}), 401
    if email != user.email or password != user.password:
        return jsonify({"msg":"Bad email or password"}), 401
    
    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token)

@api.route('/protected',methods=['GET'])
@jwt_required
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user),200

@api.route('/signup',methods=['POST'])
def signup():
    body=request.get_json()
    user=User.query.filter_by(email=body["email"]).first()
    if user != None:
        return jsonify({"msg":"Ya se encuentra creado usuario con ese correo"}), 401

    user=User(email=body["email"],password=body["password"],is_active=True)
    db.session.add(user)
    db.session.commit()
    response_body={
        "msg":"Usuario creado"
    }
    return jsonify(response_body),200