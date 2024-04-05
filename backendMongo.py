from flask import Flask, jsonify,render_template, request, session,redirect, Response
import requests
from firebase_admin import credentials, initialize_app, db , auth
import pyrebase
from auth import create_user
from pymongo import MongoClient
from dotenv import load_dotenv
import os


app = Flask(__name__)



firebaseConfig = {
    "apiKey": "AIzaSyDw-YbF7D4-WbKZIdRIi9jRgiK1N8UO-4E",
    "authDomain": "facerecog-4b4df.firebaseapp.com",
    "projectId": "facerecog-4b4df",
    "storageBucket": "facerecog-4b4df.appspot.com",
    "messagingSenderId": "170298127722",
    "appId": "1:170298127722:web:14c83c81681a7aeb2e2113",
    "measurementId": "G-C6XLLPP7Y2",
    'databaseURL':'https://facerecog-4b4df-default-rtdb.asia-southeast1.firebasedatabase.app/'
  };
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

app.secret_key  = 'secret'


# Initialize Firebase app with database URL and authentication
cred = credentials.Certificate("serviceAccountKey.json")
firebase_app = initialize_app(cred, {
    'databaseURL': 'https://facerecog-4b4df-default-rtdb.asia-southeast1.firebasedatabase.app/'
})
firebase_db = db.reference()

# Load environment variables from .env file
load_dotenv()

MONGO_USER = os.getenv('MONGO_USER')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
MONGO_CLUSTER = os.getenv('MONGO_CLUSTER')
MONGO_DATABASE = os.getenv('MONGO_DATABASE')

# MongoDB configuration
mongo_url = f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_CLUSTER}/{MONGO_DATABASE})"
database_name = MONGO_DATABASE
collection_name = os.getenv('MONGO_COLLECTION', 'movies')  # Use 'movies' as default collection name if not provided

client = MongoClient(mongo_url)
db = client[database_name]
collection = db[collection_name]

# Route to get all documents from MongoDB
@app.route('/api/data', methods=['GET'])
def get_data():
    data = list(collection.find({}, {'_id': 0}))
    return jsonify(data)

## Home page #######################################################
@app.route('/', methods=['GET'])
def home():
        return render_template('home.html')
@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/')           

## Login Page
@app.route('/Teacherlogin', methods=['POST','GET'])
def login():
    if request.method =='POST':
    # Get teacher credentials from request
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            if user:
                return redirect('/dashboard')

        except:
            return render_template('error.html')
    else:
        return render_template('login.html')



@app.route('/dashboard', methods=['GET'])
def dashboard():
    print("Welcome to DashBoard")

    # Redirect to teacher/data endpoint to fetch students data
    response = requests.get('http://localhost:5000/teacher/data', params={'emailId': user_email})
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return render_template('error.html', error=response.json()), response.status_code

# # Route to add a new document to MongoDB
# @app.route('/api/data', methods=['POST'])
# def add_data():
#     new_data = request.json
#     collection.insert_one(new_data)
#     return jsonify({'message': 'Data added successfully'})



@app.route('/teacher/data', methods=['GET'])
def get_data_by_teacher():
    email = request.args.get('emailId')
    if not email:
        return jsonify({'error': 'EmailId is required'}), 400
    students_data = list(collection.find({}, {'_id': 0}))
    for teacher in students_data:
        if teacher['emailId'] == email:
            return jsonify(teacher['students'])
    
    return jsonify({'error': 'No students found for the provided emailId'}), 404


@app.route('/add_teacher', methods=['POST','GET'])
def add_user():
    if request.method =='POST':
        # Get user credentials from request
        name = request.form.get('name')    
        email = request.form.get('email')
        password = request.form.get('password')

        # Create user with Firebase Authentication
        user_id = create_user(
            name=name,
            email=email,
            password=password
        )
        email_user = email.replace('.', '_')
        print("the user id is: ",user_id)
        if user_id:
            # Create a new database for the teacher
            teacher_ref = firebase_db.child('Teachers').child(email_user)
            teacher_ref.set({
                'email': email,
                'name': name
            })
            # Redirect to home page after successful creation
            return redirect('/')
        else:
            # Handle user creation failure
            return "Failed to register user", 500
    else:
        # Render the registration form
        return render_template('register.html')



if __name__ == '__main__':
    app.run(debug=True)
