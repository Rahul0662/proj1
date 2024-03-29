from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import json
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

users = {}
reminders = []
# Function to save users to a text file
def save_users():
    try:
        with open("users.txt", "w") as file:
            json.dump(users, file)
        print("Users saved successfully")
    except Exception as e:
        print("Error saving users:", e)

# Function to load users from a text file
def load_users():
    global users
    try:
        with open("users.txt", "r") as file:
            users = json.load(file)
        print("Loading users succeeded..")
    except FileNotFoundError:
        print("File 'users.txt' not found.")
        users = {}

# Function to authenticate users
def authenticate(username, password):
    if username in users and users[username] == password:
        return True
    return False

@app.route('/')
def index():
    global reminders

    if 'username' in session:
        reminders = load_reminders()
        return render_template('index3.html', reminders=reminders)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username not in users:
            users[username] = password
            save_users()
            flash('Registration successful. Please login.')
            return redirect(url_for('login'))
        else:
            flash('Username already exists. Please choose a different one.')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate(username, password):
            session['username'] = username
            flash('Login successful.')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))


# Function to save reminders to a text file
def save_reminders():
    try:
        path = "reminders.txt"
        with open(path, 'w') as file:
            json.dump(session['reminders'], file)
        print("Reminders saved successfully")
    except Exception as e:
        print("Error saving reminders:", e)

# Function to load reminders from a text file
def load_reminders():
    reminders = []
    try:
        with open('reminders.txt', 'r') as file:
            reminders = json.load(file)
        print("Loading reminders succeeded..")
    except FileNotFoundError:
        print("File 'reminders.txt' not found in current working directory.")
    session['reminders'] = reminders
    return reminders

# Rest of your existing code...

# Add route to handle random URL paths and redirect to login page
@app.route('/<path:path>')
def catch_all(path):
    return redirect(url_for('login'))



@app.route('/submit_form', methods=['POST'])
def submit_form():
    try:
        data = request.get_json()
        server_name = data['serverName']
        comments = data['comments']
        date = data['date']
        emails = data['email'].split(',')

        valid_emails = [email.strip() for email in emails if email.strip().endswith('@abc.com') or email.strip().endswith('@xyz.com')]
        r_len = len(reminders) + 1
        reminder = {
            'id': "reminder" + str(r_len),
            'serverName': server_name,
            'comments': comments,
            'date': date,
            'email': ', '.join(valid_emails)
        }

        reminders.append(reminder)
        save_reminders()
        return 'Reminder added successfully', 200
    except Exception as e:
        print(f"Failed to add reminder: {e}")
        return 'Failed to add reminder', 400


@app.route('/delete_reminder/<string:reminder_id>', methods=['DELETE'])
def delete_reminder(reminder_id):
    print("deleting ", reminder_id)
    global reminders
    reminders = [reminder for reminder in reminders if reminder['id'] != reminder_id]
    save_reminders()
    return jsonify({'message': 'Reminder deleted successfully'})



if __name__ == '__main__':
    load_users()
    app.run(debug=True, host='0.0.0.0', port=80)
