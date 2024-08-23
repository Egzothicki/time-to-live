import os
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta
import sqlite3  # Import the sqlite3 module

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

# Database helper functions
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_user_by_username(username):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

def update_user_death_date(username, death_date):
    conn = get_db_connection()
    conn.execute('UPDATE users SET death_date = ? WHERE username = ?', (death_date, username))
    conn.commit()
    conn.close()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')



def sanitize_input(value, default=0):
    try:
        # Try converting to integer
        int_value = int(value)
        # Cap the value if it exceeds a certain threshold
        if int_value > 10:
            return '10'
        return str(int_value)  # Return as string to match dictionary keys
    except ValueError:
        # If it's not an integer, return default as string
        return str(default)

def calculate_life_expectancy(age, gender, family_history, medical_conditions, blood_pressure,
                              cholesterol, smoker, alcohol, exercise, sleep, stress, 
                              mental_health, checkups, sun_protection, vaccinations, 
                              social_connections, pollution, occupation, substance_use):
    
    # Base life expectancy
    base_life_expectancy = 78  # Average life expectancy as baseline

    # Adjustments based on the scoring system
    adjustments = {
        'gender': {'male': -2, 'female': 0, 'other': -1},
        'family_history': {'yes': -3, 'no': 0},
        'medical_conditions': {
            'diabetes': -4,
            'heart_disease': -5,
            'cancer': -3,
            'hypertension': -2,
            'none': 0
        },
        'blood_pressure': {'yes': -3, 'no': 0},
        'cholesterol': {'yes': -3, 'no': 0},
        'smoker': {'never': 0, 'former': -3, 'current': -10},
        'alcohol': {'0': 0, '1-3': -1, '4-7': -2, '8+': -5},
        'exercise': {
            '0': -5, '1': -2, '2': -2, 
            '3': 0, '4': 0, '5': 0, 
            '6': 2, '7': 2, '8': 2, '9': 2, '10': 2
        },
        'sleep': {'less_than_5': -3, '5-6': -1, '7-8': 0, 'more_than_8': -1},
        'stress': lambda x: -0.5 * (x - 5) if x > 5 else 0,  # Deduct 0.5 years for each point above 5
        'mental_health': {'yes': -2, 'no': 0},
        'checkups': {'never': -3, 'every_few_years': -1, 'once_a_year': 0, 'more_than_once_a_year': 1},
        'sun_protection': {'never': -2, 'sometimes': -1, 'always': 0},
        'vaccinations': {'yes': 0, 'no': -2, 'not_sure': -1},
        'social_connections': {'weak': -3, 'average': 0, 'strong': 2},
        'pollution': {'yes': -3, 'no': 0, 'not_sure': -1},
        'occupation': {'yes': -2, 'no': 0},
        'substance_use': {'never': 0, 'former': -2, 'current': -5}
    }

    # Sanitize inputs
    exercise = sanitize_input(exercise)  # Sanitize exercise input

    # Apply the adjustments
    base_life_expectancy += adjustments['gender'][gender]
    base_life_expectancy += adjustments['family_history'][family_history]
    
    for condition in medical_conditions:
        base_life_expectancy += adjustments['medical_conditions'].get(condition, 0)

    base_life_expectancy += adjustments['blood_pressure'][blood_pressure]
    base_life_expectancy += adjustments['cholesterol'][cholesterol]
    base_life_expectancy += adjustments['smoker'][smoker]
    base_life_expectancy += adjustments['alcohol'][alcohol]
    base_life_expectancy += adjustments['exercise'].get(exercise, -5)  # Default to worst case if unrecognized
    base_life_expectancy += adjustments['sleep'][sleep]
    base_life_expectancy += adjustments['stress'](int(stress))
    base_life_expectancy += adjustments['mental_health'][mental_health]
    base_life_expectancy += adjustments['checkups'][checkups]
    base_life_expectancy += adjustments['sun_protection'][sun_protection]
    base_life_expectancy += adjustments['vaccinations'][vaccinations]
    base_life_expectancy += adjustments['social_connections'][social_connections]
    base_life_expectancy += adjustments['pollution'][pollution]
    base_life_expectancy += adjustments['occupation'][occupation]
    base_life_expectancy += adjustments['substance_use'][substance_use]

    # Calculate the remaining years
    years_left = base_life_expectancy - int(age)
    if years_left < 0:
        years_left = 0

    # Calculate the number of days, including the fractional part
    total_days_left = years_left * 365.25

    # Calculate the future date of death including the exact current time
    death_date = datetime.now() + timedelta(days=total_days_left)

    return death_date

def save_user(username, password):
    with open(USER_FILE, 'a') as file:
        file.write(f'{username},{password}\n')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = get_user_by_username(username)

        if user and user['password'] == password:
            session['username'] = username
            death_date = user['death_date']

            # Check if the user has already completed the questionnaire
            if death_date:
                return redirect(url_for('results'))  # Redirect to the countdown page
            else:
                return redirect(url_for('questionnaire'))  # Redirects to questionnaire
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if get_user_by_username(username):
            return render_template('register.html', error="Username already exists")

        conn = get_db_connection()
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/questionnaire')
def questionnaire():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('questionnaire.html')

@app.route('/time-to-live', methods=['POST'])
def submit_questionnaire():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Retrieve form data
    age = request.form['age']
    gender = request.form['gender']
    height = request.form['height']
    height_unit = request.form['height_unit']
    weight = request.form['weight']
    weight_unit = request.form['weight_unit']
    family_history = request.form['family_history']
    medical_conditions = request.form.getlist('medical_conditions')
    blood_pressure = request.form['blood_pressure']
    cholesterol = request.form['cholesterol']
    smoker = request.form['smoker']
    alcohol = request.form['alcohol']
    exercise = request.form['exercise']
    sleep = request.form['sleep']
    stress = request.form['stress']
    mental_health = request.form['mental_health']
    checkups = request.form['checkups']
    sun_protection = request.form['sun_protection']
    vaccinations = request.form['vaccinations']
    social_connections = request.form['social_connections']
    pollution = request.form['pollution']
    occupation = request.form['occupation']
    substance_use = request.form['substance_use']

    # Convert height to cm if needed
    if height_unit == "inches":
        height_cm = int(height) * 2.54  # Convert inches to cm
    else:
        height_cm = int(height)  # Already in cm

    # Convert weight to kg if needed
    if weight_unit == "lbs":
        weight_kg = int(weight) * 0.453592  # Convert lbs to kg
    else:
        weight_kg = int(weight)  # Already in kg

    # Calculate life expectancy
    death_date = calculate_life_expectancy(
        age, gender, family_history, medical_conditions, blood_pressure,
        cholesterol, smoker, alcohol, exercise, sleep, stress, 
        mental_health, checkups, sun_protection, vaccinations, 
        social_connections, pollution, occupation, substance_use
    )
    
    # Format the death_date to a string format that JavaScript can easily parse
    death_date_str = death_date.strftime('%Y-%m-%dT%H:%M:%S')

    update_user_death_date(session['username'], death_date_str)

    # Redirect to the results page to display the countdown
    return redirect(url_for('results'))

@app.route('/next_step')
def next_step():
    if 'username' in session:
        return redirect(url_for('questionnaire'))
    else:
        return redirect(url_for('login'))

@app.route('/results')
def results():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Load the user's data from the database
    user = get_user_by_username(session['username'])
    death_date = user['death_date']

    if death_date:
        return render_template('results.html', death_date=death_date)
    else:
        return redirect(url_for('questionnaire'))

if __name__ == '__main__':
    app.run(debug=True)