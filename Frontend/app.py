import os
import joblib
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB and Login Manager
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Load ML Models globally
try:
    model = joblib.load('best_rf_model.pkl')
    scaler_X = joblib.load('scaler_X.pkl')
    scaler_y = joblib.load('scaler_y.pkl')
    print("Models loaded successfully!")
except FileNotFoundError as e:
    print(f"Warning: Model files not found - {e}")
    model, scaler_X, scaler_y = None, None, None

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes ---

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('signup'))
        
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('predict'))
        else:
            flash('Invalid username or password', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    if request.method == 'POST':
        try:
            # Check which input method was used
            input_method = request.form.get('input_method')
            
            if input_method == 'single':
                # Single text area input - all 18 values
                all_values = request.form.get('all_features')
                # Split by space, comma, or tab
                values_list = [float(x.strip()) for x in all_values.replace(',', ' ').replace('\t', ' ').split()]
                
                if len(values_list) != 18:
                    flash(f'Expected 18 values, got {len(values_list)}', 'danger')
                    return redirect(url_for('predict'))
                
                data_dict = {
                    'Temperature': values_list[0],
                    'Humidity': values_list[1],
                    'SquareFootage': values_list[2],
                    'Occupancy': values_list[3],
                    'RenewableEnergy': values_list[4],
                    'HVACUsage_Off': values_list[5],
                    'HVACUsage_On': values_list[6],
                    'LightingUsage_Off': values_list[7],
                    'LightingUsage_On': values_list[8],
                    'DayOfWeek_Friday': values_list[9],
                    'DayOfWeek_Monday': values_list[10],
                    'DayOfWeek_Saturday': values_list[11],
                    'DayOfWeek_Sunday': values_list[12],
                    'DayOfWeek_Thursday': values_list[13],
                    'DayOfWeek_Tuesday': values_list[14],
                    'DayOfWeek_Wednesday': values_list[15],
                    'Holiday_No': values_list[16],
                    'Holiday_Yes': values_list[17]
                }
            else:
                # Individual field input
                data_dict = {
                    'Temperature': float(request.form.get('Temperature')),
                    'Humidity': float(request.form.get('Humidity')),
                    'SquareFootage': float(request.form.get('SquareFootage')),
                    'Occupancy': int(request.form.get('Occupancy')),
                    'RenewableEnergy': int(request.form.get('RenewableEnergy')),
                    'HVACUsage_Off': int(request.form.get('HVACUsage_Off')),
                    'HVACUsage_On': int(request.form.get('HVACUsage_On')),
                    'LightingUsage_Off': int(request.form.get('LightingUsage_Off')),
                    'LightingUsage_On': int(request.form.get('LightingUsage_On')),
                    'DayOfWeek_Friday': int(request.form.get('DayOfWeek_Friday')),
                    'DayOfWeek_Monday': int(request.form.get('DayOfWeek_Monday')),
                    'DayOfWeek_Saturday': int(request.form.get('DayOfWeek_Saturday')),
                    'DayOfWeek_Sunday': int(request.form.get('DayOfWeek_Sunday')),
                    'DayOfWeek_Thursday': int(request.form.get('DayOfWeek_Thursday')),
                    'DayOfWeek_Tuesday': int(request.form.get('DayOfWeek_Tuesday')),
                    'DayOfWeek_Wednesday': int(request.form.get('DayOfWeek_Wednesday')),
                    'Holiday_No': int(request.form.get('Holiday_No')),
                    'Holiday_Yes': int(request.form.get('Holiday_Yes'))
                }

            # Create DataFrame
            new_data = pd.DataFrame([data_dict])
            
            # Scale and Predict
            new_data_scaled = scaler_X.transform(new_data)
            prediction_scaled = model.predict(new_data_scaled)
            
            # Inverse Transform
            prediction_actual = scaler_y.inverse_transform(prediction_scaled.reshape(-1, 1))
            result_value = prediction_actual[0][0]

            session['prediction_result'] = f"{result_value:.2f}"
            return redirect(url_for('result'))

        except Exception as e:
            flash(f'Prediction Error: {str(e)}', 'danger')
            return redirect(url_for('predict'))

    return render_template('predict.html')

@app.route('/result')
@login_required
def result():
    pred = session.get('prediction_result', 'No prediction found')
    return render_template('result.html', prediction=pred)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create DB tables
    app.run(debug=True)