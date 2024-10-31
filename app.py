from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_mysqldb import MySQL
from flask_cors import CORS
from config import Config
from models.user_model import UserModel

app = Flask(__name__)
app.config.from_object(Config)

# Allow CORS for specific methods
CORS(app, resources={r"/*": {"origins": "http://localhost:5173", "methods": ["GET", "POST", "PUT", "DELETE"]}})
mysql = MySQL(app)
jwt = JWTManager(app)

user_model = UserModel(mysql)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = "customer"
    
    user_model.register_user(name, email, password, role)
    return jsonify(message="User registered successfully"), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    name = data.get('name')
    password = data.get('password')

    user = user_model.find_user_by_name(name)
    if user and user_model.verify_password(user[1], password):
        access_token = create_access_token(identity={'name': name, 'user_id': user[0]})
        return jsonify(
            access_token=access_token, 
            name=name, 
            user_id=user[0],
            role=user[2]
        ), 200

    return jsonify(message="Invalid credentials"), 401

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = user_model.get_user_by_id(user_id)
    if user:
        return jsonify({
            'name': user[0],
            'email': user[1],
            'role': user[2]
        }), 200
    else:
        return jsonify(message="User not found"), 404

@app.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    print(f"Updating user with ID: {user_id}")  # Debugging statement
    data = request.get_json()
    name = data.get('name')  # Optional
    email = data.get('email')  # Optional
    password = data.get('password')  # Optional

    # Validate user existence
    user = user_model.get_user_by_id(user_id)
    if not user:
        return jsonify(message="User not found"), 404

    # Update user data
    if name:
        user_model.update_user_name(user_id, name)  # Ensure this method exists in UserModel
    if email:
        user_model.update_user_email(user_id, email)  # Ensure this method exists in UserModel
    if password:
        user_model.update_user_password(user_id, password)  # Ensure this method exists in UserModel

    return jsonify(message="User updated successfully"), 200

@app.route('/users/customers', methods=['GET'])
@jwt_required()
def get_customers():
    try:
        customers = user_model.get_users_by_role('customer')
        # Format the data for the response
        customer_list = [{'id': customer[0], 'name': customer[1], 'email': customer[2]} for customer in customers]
        return jsonify(customer_list), 200
    except Exception as e:
        print(f"Error fetching customers: {e}")  # Debugging statement
        return jsonify(message="An error occurred while fetching users."), 500
    
@app.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    # Check if user exists
    user = user_model.get_user_by_id(user_id)
    if not user:
        return jsonify(message="User not found"), 404

    # Delete user
    if user_model.delete_user(user_id):
        return jsonify(message="User deleted successfully"), 200
    else:
        return jsonify(message="An error occurred while deleting the user"), 500

if __name__ == "__main__":
    app.run(debug=True)
