from flask import Flask, jsonify, request, url_for, send_from_directory
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_mysqldb import MySQL
from flask_cors import CORS
from config import Config
from models.user_model import UserModel
from models.admin_service_modal import AdminServiceModel
from models.product_model import ProductModel
import os
from werkzeug.utils import secure_filename
from transformers import AutoModelForImageClassification
from PIL import Image
import torch
import torchvision.transforms as transforms
from models.haircut_model import HaircutModel

app = Flask(__name__)
app.config.from_object(Config)

model = AutoModelForImageClassification.from_pretrained("TharushikaD/facecut_me")
model.eval()  

preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
])


UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

CORS(app, resources={r"/*": {"origins": "http://localhost:5173", "methods": ["GET", "POST", "PUT", "DELETE"]}})
mysql = MySQL(app)
jwt = JWTManager(app)

user_model = UserModel(mysql)
admin_service_model = AdminServiceModel(mysql)
product_model = ProductModel(mysql, base_url="http://127.0.0.1:5000")
haircut_model = HaircutModel(mysql, base_url="http://127.0.0.1:5000")

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
    print(f"Updating user with ID: {user_id}")  
    data = request.get_json()
    name = data.get('name')  
    email = data.get('email') 
    password = data.get('password')  

   
    user = user_model.get_user_by_id(user_id)
    if not user:
        return jsonify(message="User not found"), 404

    
    if name:
        user_model.update_user_name(user_id, name)  
    if email:
        user_model.update_user_email(user_id, email)  
    if password:
        user_model.update_user_password(user_id, password)  

    return jsonify(message="User updated successfully"), 200

@app.route('/users/customers', methods=['GET'])
@jwt_required()
def get_customers():
    try:
        customers = user_model.get_users_by_role('customer')
        customer_list = [{'id': customer[0], 'name': customer[1], 'email': customer[2]} for customer in customers]
        return jsonify(customer_list), 200
    except Exception as e:
        print(f"Error fetching customers: {e}")  
        return jsonify(message="An error occurred while fetching users."), 500

@app.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
   
    user = user_model.get_user_by_id(user_id)
    if not user:
        return jsonify(message="User not found"), 404

   
    if user_model.delete_user(user_id):
        return jsonify(message="User deleted successfully"), 200
    else:
        return jsonify(message="An error occurred while deleting the user"), 500

@app.route('/services', methods=['POST'])
@jwt_required()
def add_service():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    
    admin_service_model.add_service(name, description, price)
    return jsonify(message="Service added successfully"), 201

@app.route('/services/<int:service_id>', methods=['PUT'])
@jwt_required()
def update_service(service_id):
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    
    admin_service_model.update_service(service_id, name, description, price)
    return jsonify(message="Service updated successfully"), 200

@app.route('/services/<int:service_id>', methods=['DELETE'])
@jwt_required()
def delete_service(service_id):
    if admin_service_model.delete_service(service_id):
        return jsonify(message="Service deleted successfully"), 200
    else:
        return jsonify(message="An error occurred while deleting the service"), 500

@app.route('/services', methods=['GET'])
def get_services():
    services = admin_service_model.get_all_services()
    service_list = [{'id': service[0], 'name': service[1], 'description': service[2], 'price': service[3]} for service in services]
    return jsonify(service_list), 200

# Manage products
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/products', methods=['POST'])
@jwt_required()
def add_product():
    product_name = request.form.get('product_name')
    description = request.form.get('description')
    category = request.form.get('category')
    price = request.form.get('price')

   
    image = request.files.get('image')
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)
        
        
        image_url = url_for('uploaded_file', filename=filename, _external=True)
    else:
        image_url = '' 

    product_model.add_product(product_name, description, category, price, image_url)
    return jsonify({'message': 'Product added successfully!'}), 201

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/products', methods=['GET'])
def get_products():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM products")
        results = cur.fetchall()
        
        print("Raw results from database:", results)  
        
        products = []
        for result in results:
            products.append({
                'id': result[0],
                'product_name': result[1],
                'description': result[2],
                'category': result[3],
                'price': result[4],
                'image_url': result[5]
            })
        
        print("Formatted products:", products)  
        
        return jsonify(products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()

@app.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    data = request.get_json()
    product_model.update_product(
        product_id,
        product_name=data['product_name'],
        description=data['description'],
        category=data['category'],
        price=data['price'],
        image_url=data['image_url']
    )
    return jsonify({'message': 'Product updated successfully!'})

@app.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    product_model.delete_product(product_id)
    return jsonify({'message': 'Product deleted successfully!'})


@app.route('/detect-face-shape', methods=['POST'])
def detect_face_shape():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400

        file = request.files['image']
        image = Image.open(file.stream).convert("RGB")
        image_tensor = preprocess(image).unsqueeze(0)
        
      
        print("Image tensor shape:", image_tensor.shape)  

        with torch.no_grad():
            output = model(image_tensor)
            probabilities = torch.nn.functional.softmax(output.logits, dim=1)
            predicted_class = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0, predicted_class].item()

            print("Predicted class:", predicted_class)
            print("Confidence:", confidence)

           
            face_shape_mapping = {
                0: 'Actress Heart Face',
                1: 'Actress Oval Face',
                2: 'Actress Round Face',
                3: 'Actress Square Face'
            }

            
            detected_face_shape = face_shape_mapping.get(predicted_class, 'Unknown')
            print("Detected face shape:", detected_face_shape)
            recommended_haircuts = haircut_model.get_haircuts_by_face_shape(detected_face_shape)

        return jsonify({
            'predicted_class': predicted_class,
            'detected_face_shape': detected_face_shape,
            'confidence': confidence,
            'recommended_haircuts': recommended_haircuts
        })
    except Exception as e:
        print("Error in detect_face_shape:", str(e))  
        return jsonify({'error': str(e)}), 500


# HairCut Management
@app.route('/haircuts', methods=['GET'])
def get_all_haircuts():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM haircuts")  
        results = cur.fetchall()
        
        print("Raw results from database:", results)  
        
        haircuts = []
        for result in results:
            haircuts.append({
                'id': result[0],
                'haircut_name': result[1],
                'description': result[2],
                'face_shape': result[3],
                'image_url': result[4]  
            })
        
        print("Formatted haircuts:", haircuts)  
        
        return jsonify(haircuts), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()

@app.route('/haircutss', methods=['GET'])
def get_haircuts():
    face_shape = request.args.get('face_shape')
    if face_shape:
        haircuts = haircut_model.get_haircuts_by_face_shape(face_shape)
        return jsonify(haircuts)
    return jsonify({'error': 'Face shape not provided'}), 400


@app.route('/haircuts', methods=['POST'])
@jwt_required() 
def add_haircut():
    face_shape = request.form.get('face_shape')
    haircut_name = request.form.get('haircut_name')
    description = request.form.get('description', '')

    
    image = request.files.get('image')
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)

       
        image_url = url_for('uploaded_file', filename=filename, _external=True)
    else:
        image_url = ''  

    success = haircut_model.add_haircut(face_shape, haircut_name, description, image_url)
    return jsonify({'success': success}), 201 if success else 400


@app.route('/haircuts/<int:haircut_id>', methods=['PUT'])
@jwt_required()  
def update_haircut(haircut_id):
    face_shape = request.form.get('face_shape')
    haircut_name = request.form.get('haircut_name')
    description = request.form.get('description', '')

    
    image = request.files.get('image')
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)

        
        image_url = url_for('uploaded_file', filename=filename, _external=True)
    else:
        image_url = None  

    success = haircut_model.update_haircut(haircut_id, face_shape, haircut_name, description, image_url)
    return jsonify({'success': success}), 200 if success else 400


@app.route('/haircuts/<int:haircut_id>', methods=['DELETE'])
@jwt_required() 
def delete_haircut(haircut_id):
    success = haircut_model.delete_haircut(haircut_id)
    return jsonify({'success': success}), 200 if success else 404



if __name__ == "__main__":
    app.run(debug=True)
