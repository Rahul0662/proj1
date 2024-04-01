from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import json
import os
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from otp import generate_otp, store_otp, get_otp, clear_otp
from myssh import send_email
import schedule
import threading
import time
import pytz

app = Flask(__name__)
app.secret_key = os.urandom(24)

users_file = "users.txt"
reminders_file = "reminders.txt"

users = []
reminders = {}


def handle_all_email(sub, body, recipients):
    print(f"sending mail {sub} ,{body},{recipients}")
    return send_email(sub, body, recipients)


def save_data(file_path, data):
    try:
        with open(file_path, "w") as file:
            json.dump(data, file)
        print(f"Data saved successfully to {file_path}")
    except Exception as e:
        print(f"Error saving data to {file_path}: {e}")


def load_data(file_path):
    data = {}
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        print(f"Data loaded successfully from {file_path}")
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    return data


def save_users():
    save_data(users_file, users)


def load_users():
    global users
    users = load_data(users_file)


def save_reminders():
    save_data(reminders_file, reminders)


def load_reminders():
    global reminders
    reminders = load_data(reminders_file)


@app.before_request
def load_session_data():
    print("load_session_data...")
    load_users()
    load_reminders()


@app.route('/')
def index():
    if 'email' in session:
        return render_template('index4.html', reminders=reminders)
    return redirect(url_for('login'))


def find_username(username):
    for user in users:
        if user['username'] == username:
            return True
    return False


def find_email(email):
    for user in users:
        if user['email'] == email:
            return True
    return False


def generate_user_otp(email, content_t):
    otp = generate_otp()
    print("OTP :- ", otp)
    msg = f" OTP  : {otp}"
    store_otp(email, otp)
    return handle_all_email(content_t, msg, email)


# other routes and functions...
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if not (find_username(username) or find_email(email)):

            status = generate_user_otp(email, "Registration Email Validation")

            # Hash password
            hashed_password = generate_password_hash(password)

            # Add user to database
            j_user = {
                'username': username,
                'email': email,
                'password': hashed_password,
                'verified': "False"
            }
            users.append(j_user)
            save_users()
            if status:
                flash(f'Registration successful. Please verify your email address with the OTP sent. ')
            else:
                flash(f'Registration successful. Failed to send OTP ')
            return redirect(url_for('verify_email', email=email))
        else:
            flash('Username or email already exists. Please choose a different one.')
    return render_template('register.html')


@app.route('/verify_email', methods=['GET', 'POST'])
def verify_email():
    if request.method == 'POST':
        email = request.form['email']
        user = find_user(email)
        user_otp = request.form['otp']
        stored_otp = get_otp(email)
        if stored_otp == user_otp:
            user['verified'] = "True"
            update_user_in_users_list(user)
            clear_otp(email)  # Clear OTP after successful verification
            flash('Email verification successful. You can now login.')
            return redirect(url_for('login'))
        else:
            flash('Invalid OTP. Please try again.')
    email = request.args.get('email')
    return render_template('verify_email.html', email=email)


def authenticate(email, password):
    for user in users:
        if user['email'] == email:
            if check_password_hash(user['password'], password):
                return True
    return False


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'email' in session:
        # Redirect to home page if already logged in
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print("authentication check - ", authenticate(email, password))
        if authenticate(email, password):
            user = find_user(email)
            print(user)
            if user['verified'] != "True":
                print("condition true - verified user")
                generate_user_otp(email, "Email Verification")
                return redirect(url_for('verify_email', email=email))
            session['email'] = user['email']
            flash('Login successful.')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('email', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))


@app.route('/<path:path>')
def catch_all(path):
    return redirect(url_for('login'))


def epoch_to_string(epoch_time_ms):
    # Convert milliseconds to seconds
    epoch_time_sec = epoch_time_ms / 1000

    # Convert epoch time to timezone-aware datetime object
    datetime_obj = datetime.datetime.fromtimestamp(epoch_time_sec, datetime.timezone.utc)

    # Format the datetime object as a string
    formatted_string = datetime_obj.strftime('%Y-%m-%d %H:%M:%S')

    return formatted_string


@app.route('/submit_form', methods=['POST'])
def submit_form():
    try:
        data = request.get_json()
        activity_name = data['activityName']
        ticket = data['ticket']
        comments = data['comments']
        epoch = data['date']
        emails = data['emails'].split(',')
        print(epoch)
        valid_emails = [email.strip() for email in emails if
                        email.strip().endswith('@abc.com') or email.strip().endswith('@xyz.com')]
        r_len = len(reminders) + 1
        # date_string = datetime.today().strftime('%Y-%m-%d')
        date_string = epoch_to_string(epoch)
        print(date_string)
        email = session['email']

        current_datetime_gmt = datetime.datetime.now(pytz.timezone('GMT'))

        current_datetime = datetime.datetime.now()
        formatted_current_datetime_gmt = current_datetime_gmt.strftime('%Y-%m-%d %H:%M:%S')

        reminder = {
            'id': "reminder" + str(r_len),
            'activityName': activity_name,
            'ticket': ticket,
            'comments': comments,
            'date': date_string,
            'epoch': epoch,
            'email': session['email'],
            'author': email,
            'log_date': formatted_current_datetime_gmt,
            'emails': ', '.join(valid_emails)
        }

        reminders.append(reminder)
        save_reminders()
        return 'Reminder added successfully', 200
    except Exception as e:
        print(f"Failed to add reminder: {e}")
        return 'Failed to add reminder', 400


@app.route('/delete_reminder/<string:reminder_id>', methods=['DELETE'])
def delete_reminder(reminder_id):
    global reminders
    reminders = [reminder for reminder in reminders if reminder['id'] != reminder_id]
    save_reminders()
    return jsonify({'message': 'Reminder deleted successfully'})


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')

        # Check if email is provided
        if not email:
            flash('Email is required.', 'error')
            return redirect(url_for('forgot_password'))

        # Check if email is registered
        if not any(user.get('email') == email for user in users):
            flash('Email not registered.', 'error')
            return redirect(url_for('forgot_password'))

        status = generate_user_otp(email, "reset password ")
        if status:
            flash('An OTP has been sent to your email.', 'success')
            return redirect(url_for('verify_otp', email=email))
        else:
            flash(f'Failed to send OTP email. ', 'error')
            return redirect(url_for('forgot_password'))

    return render_template('forgot_password.html')


@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    email = request.args.get('email')
    # Check if email is provided
    if not email:
        flash('Email is required.', 'error')
        return redirect(url_for('forgot_password'))

    # Check if OTP is provided
    if request.method == 'POST':
        user_otp = request.form.get('otp')
        if not user_otp:
            flash('OTP is required.', 'error')
            return redirect(url_for('verify_otp', email=email))

        stored_otp = get_otp(email)
        if stored_otp == user_otp:
            clear_otp(email)  # Clear OTP after successful verification
            session['reset_email'] = email  # Store email in session for password reset
            return redirect(url_for('reset_password', email=email))
        else:
            flash('Invalid OTP. Please try again.', 'error')
            return redirect(url_for('verify_otp', email=email))

    return render_template('verify_otp.html', email=email)


def find_user(email):
    for user in users:
        if user['email'] == email:
            return user
    return None


def update_user_in_users_list(updated_user):
    global users
    for index, user in enumerate(users):
        if user['email'] == updated_user['email'] or user['username'] == updated_user['username']:
            users[index] = updated_user
            save_users()
            break


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    email = request.args.get('email')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        user = find_user(email)

        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('reset_password'))

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('reset_password'))

        # Update password for the user
        user['password'] = generate_password_hash(password)
        update_user_in_users_list(user)
        flash('Password updated successfully.')
        return redirect(url_for('login'))

    return render_template('reset_password.html', email=email)


# Background task to run the scheduler
def scheduler_task():
    while True:
        schedule.run_pending()
        time.sleep(2)  # Sleep for a short interval to avoid high CPU usage


# Function to check if the reminder datetime is close to the current datetime
import time

import time


def check_reminders():
    current_epoch_milliseconds = int(time.time()) * 1000  # Current time in milliseconds
    for reminder in reminders:
        reminder_epoch_milliseconds = reminder['epoch']
        print(f"reminders Epoch - {reminder_epoch_milliseconds} , current Epoch -  {current_epoch_milliseconds}")
        if abs(reminder_epoch_milliseconds - current_epoch_milliseconds) < 10000:  # 10 seconds in milliseconds
            handle_all_email(reminder['activityName'], reminder['comments'], reminder['emails'])


# Function to schedule the reminder check
def schedule_reminder_check():
    print("schedule_reminder_check()")
    schedule.every(10).seconds.do(check_reminders)


if __name__ == '__main__':
    schedule_reminder_check()
    scheduler_thread = threading.Thread(target=scheduler_task)
    scheduler_thread.start()
    app.run(debug=True, host='0.0.0.0', port=80)
