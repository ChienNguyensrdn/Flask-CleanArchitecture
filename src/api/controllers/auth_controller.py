import jwt
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta, timezone
from functools import wraps

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def token_required(f):
    """Decorator to protect routes with JWT authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401
        
        try:
            payload = jwt.decode(
                token, 
                current_app.config['SECRET_KEY'], 
                algorithms=['HS256']
            )
            request.current_user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token"""
    from infrastructure.models.user_model import UserModel
    from infrastructure.databases.mssql import get_session
    
    data = request.get_json()
    
    # Validate input
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    username = data.get('user_name')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    try:
        session = get_session()
        user = session.query(UserModel).filter_by(user_name=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.status:
            return jsonify({'error': 'Account is disabled'}), 403

        payload = {
            'user_id': user.id,
            'user_name': user.user_name,
            'exp': datetime.now(timezone.utc) + timedelta(hours=2),
            'iat': datetime.now(timezone.utc)
        }
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'token': token,
            'user_id': user.id,
            'user_name': user.user_name,
            'expires_in': 7200  # 2 hours in seconds
        })
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Authentication failed'}), 500
    finally:
        session.close()


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    from infrastructure.models.user_model import UserModel
    from infrastructure.databases.mssql import get_session
    from datetime import datetime, timezone
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body is required'}), 400
    
    username = data.get('user_name')
    password = data.get('password')
    description = data.get('description', '')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    
    try:
        session = get_session()
        
        # Check if user already exists
        existing_user = session.query(UserModel).filter_by(user_name=username).first()
        if existing_user:
            return jsonify({'error': 'Username already exists'}), 409
        
        # Create new user
        user = UserModel(
            user_name=username,
            description=description,
            status=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        user.set_password(password)
        
        session.add(user)
        session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user.id,
            'user_name': user.user_name
        }), 201
    except Exception as e:
        session.rollback()
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500
    finally:
        session.close()


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    """Get current authenticated user info"""
    from infrastructure.models.user_model import UserModel
    from infrastructure.databases.mssql import get_session
    
    try:
        session = get_session()
        user = session.query(UserModel).filter_by(id=request.current_user_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user_id': user.id,
            'user_name': user.user_name,
            'description': user.description,
            'status': user.status
        })
    finally:
        session.close()