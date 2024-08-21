import os
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

# File to store user credentials
USER_FILE = 'users.txt'

from datetime import datetime, timedelta

def calculate_life_expectancy(age, gender, smoker, exercise):
    # Base life expectancy (for simplicity, we use a starting value)
    base_life_expectancy = 80

    # Adjust life expectancy based on gender
    if gender == "male":
        base_life_expectancy -= 3.17  # Adjust as needed
    elif gender == "female":
        base_life_expectancy += 2.32

    # Adjust life expectancy based on smoker status
    if smoker == "yes":
        base_life_expectancy -= 10.53  # Using a fractional value for testing
    else:
        base_life_expectancy += 0  # No change for non-smokers

    # Adjust life expectancy based on exercise frequency
    if int(exercise) >= 3:
        base_life_expectancy += 3.42
    elif int(exercise) == 0:
        base_life_expectancy -= 5.11

    # Calculate the remaining years (could be fractional)
    years_left = base_life_expectancy - int(age)
    if years_left < 0:
        years_left = 0

    # Calculate the number of days, including the fractional part
    total_days_left = years_left * 365.25

    # Calculate the future date of death including the exact current time
    death_date = datetime.now() + timedelta(days=total_days_left)

    return death_date

def load_users():
    users = {}
    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r') as file:
            for line in file:
                username, password = line.strip().split(',')
                users[username] = password
    return users

def save_user(username, password):
    with open(USER_FILE, 'a') as file:
        file.write(f'{username},{password}\n')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    users = load_users()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('questionnaire'))  # Redirects to questionnaire
        else:
            return "Invalid credentials", 401

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    users = load_users()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users:
            return "Username already exists", 400
        
        save_user(username, password)  # Save the new user to users.txt
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

    age = request.form['age']
    gender = request.form['gender']
    smoker = request.form['smoker']
    exercise = request.form['exercise']

    death_date = calculate_life_expectancy(age, gender, smoker, exercise)
    
    # Format the death_date to a string format that JavaScript can easily parse
    death_date_str = death_date.strftime('%Y-%m-%dT%H:%M:%S')
    
    return render_template('results.html', death_date=death_date_str)

@app.route('/next_step')
def next_step():
    if 'username' in session:
        return redirect(url_for('questionnaire'))
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)