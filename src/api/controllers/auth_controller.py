import jwt
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    # Import here to avoid circular imports
    from infrastructure.models.user_model import UserModel
    from infrastructure.databases.mssql import session
    
    data = request.get_json()
    user = session.query(UserModel).filter_by(
        user_name=data['user_name'],
        password=data['password']
    ).first()
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(hours=2)
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'token': token})