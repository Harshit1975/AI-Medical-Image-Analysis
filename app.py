from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import tensorflow as tf
import numpy as np
import cv2
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = 'super_secret_medical_ai_key_2026'

# Path to the trained model
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'medical_ai_model.h5')

# Attempt to load model on startup
model = None
if os.path.exists(MODEL_PATH):
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        print("Medical Diagnostic Model successfully loaded.")
    except Exception as e:
        print(f"Error loading model: {e}")
else:
    print(f"Warning: Model not found at '{MODEL_PATH}'. Please train the model and save it to this location first.")

# Database setup
DB_FILE = 'users.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    # Users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Scans History & Mock Patients table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            patient_name TEXT,
            age_sex TEXT,
            timestamp TEXT NOT NULL,
            confidence REAL,
            outcome TEXT,
            status_label TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the Database
init_db()

@app.route('/')
def index():
    """Renders the main clinical dashboard."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html', user=session.get('user_name', 'Physician'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Renders the login page and handles authentication."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['logged_in'] = True
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Renders the registration page and handles new user creation."""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not name or not email or not password:
            flash('All fields are required.')
            return redirect(url_for('register'))
            
        hashed_password = generate_password_hash(password)
        
        try:
            conn = get_db_connection()
            conn.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, hashed_password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists. Please log in.')
            return redirect(url_for('register'))
            
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Clears the session and logs the user out."""
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/dashboard_data', methods=['GET'])
def get_dashboard_data():
    """Returns aggregated states and recent history for the dynamic UI."""
    if not session.get('logged_in'):
         return jsonify({"error": "Unauthorized"}), 401
         
    conn = get_db_connection()
    scans = conn.execute('SELECT * FROM scans ORDER BY id DESC LIMIT 50').fetchall()
    conn.close()
    
    scan_list = [dict(s) for s in scans]
    
    total_scans = len(scan_list)
    risk_detections = sum(1 for s in scan_list if s['status_label'] == 'danger')
    
    # Insights distribution
    pneumonia_pct = round((risk_detections / total_scans * 100)) if total_scans > 0 else 0
    normal_pct = 100 - pneumonia_pct if total_scans > 0 else 0
    
    return jsonify({
        "total_scans": total_scans,
        "high_risk": risk_detections,
        "pneumonia_pct": pneumonia_pct,
        "normal_pct": normal_pct,
        "history": scan_list
    })

@app.route('/predict', methods=['POST'])
def predict():
    """API Endpoint to receive an image, return diagnostic prediction, and log to DB."""
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided."}), 400
        
    if model is None:
         return jsonify({"error": "AI Model not loaded. Please ensure medical_ai_model.h5 exists in the models folder."}), 500

    try:
        file = request.files['image'].read()
        
        # 1. Convert byte stream to numpy array
        npimg = np.frombuffer(file, np.uint8)
        
        # 2. Decode image to grayscale matrix
        image = cv2.imdecode(npimg, cv2.IMREAD_GRAYSCALE)
        
        if image is None:
             return jsonify({"error": "Invalid image file."}), 400
             
        # 3. Preprocess for the CNN (Resize to 256x256, Normalize 0-1)
        image = cv2.resize(image, (256, 256))
        image = image / 255.0
        image = image.reshape(1, 256, 256, 1)
        
        # 4. Model Inference
        prediction = model.predict(image)[0][0]
        
        # 5. Interpret Score
        confidence = float(prediction if prediction > 0.5 else 1 - prediction)
        confidence_percentage = round(confidence * 100, 2)
        
        result_text = "Pneumonia Detected" if prediction > 0.5 else "Normal (Healthy)"
        status = "danger" if prediction > 0.5 else "success"
        
        # 6. MOCK PATIENT DATA INJECTION & LOGGING
        # Map the scanned patient name directly to the logged in user to make it personal
        mock_name = session.get('user_name', 'Anonymous Patient')
        mock_id = f"#PX-{random.randint(1000, 9999)}"
        mock_age_sex = f"{random.randint(18, 85)} / {random.choice(['M', 'F'])}"
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO scans (patient_id, patient_name, age_sex, timestamp, confidence, outcome, status_label) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (mock_id, mock_name, mock_age_sex, now_str, confidence_percentage, result_text, status))
        conn.commit()
        conn.close()
        
        return jsonify({
            "diagnosis": result_text,
            "confidence": confidence_percentage,
            "status": status,
            "raw_score": float(prediction)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
