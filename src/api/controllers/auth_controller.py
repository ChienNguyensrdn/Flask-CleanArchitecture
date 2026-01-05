import jwt
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
from infrastructure.models.user_model import UserModel
from infrastructure.databases.mssql import session
from api.schemas.auth import RigisterUserRequestSchema,RigisterUserResponseSchema
from services.auth_service import AuthService
from infrastructure.repositories.auth_repository import AuthRepository

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
auth_service = AuthService(AuthRepository(session))
register_request = RigisterUserRequestSchema()
register_response = RigisterUserResponseSchema()
@auth_bp.route('/check_router', methods=['GET'])
def check_router():
    """
    Check router
    ---
    get:
      summary: Check router health
      tags:
        - Auth
      responses:
        200:
          description: Router is working
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
    """
    return jsonify({'message': 'Router is working!'}), 200

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user
    ---
    post:
      summary: Login user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/LoginUserRequest'
      tags:
        - Auth
      responses:
        200:
          description: Successful login
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LoginUserResponse'
        401:
          description: Invalid credentials
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
    """
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


@auth_bp.route('/signup', methods=['POST'])
def register():
    """
    Register a new user
    ---
    post:
      summary: Register a new user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RigisterUserRequest'
      tags:
        - Auth
      responses:
        201:
          description: User registered successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RigisterUserResponse'
        400:
          description: Invalid input or user exists
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
    """
    data = request.get_json()
    errors = register_request.validate(data)
    if errors:
        return jsonify(errors), 400
    # Lay thong tin tu nguoi dung truyen vao
    
    
    if request.method == 'POST':
        user_name = request.form['user_name']
        password = request.form['password']
        password_confirm = request.form['password_confirm']


        if auth_service.check_exist(user_name):
            return jsonify({'message': 'User already exists. Please login.'}), 400

    #     hashed_password = generate_password_hash(password)
    #     new_user = User(public_id=str(uuid.uuid4()), name=name, email=email, password=hashed_password)

    #     db.session.add(new_user)
    #     db.session.commit()

    #     return redirect(url_for('login'))

    # return render_template('register.html')