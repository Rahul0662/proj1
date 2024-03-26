from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
import html
app = Flask(__name__)

reminders = []


# Function to save reminders to a text file
def save_reminders():
    try:
        path = "reminders.txt"
        with open(path, 'w') as file:
            json.dump(reminders, file)
        print("Reminders saved successfully")
    except Exception as e:
        print("Error saving reminders:", e)

# Function to load reminders from a text file
def load_reminders():
    print("inside load_reminders")
    global reminders
    try:
        with open('reminders.txt', 'r') as file:
            reminders = json.load(file)
        print("Loading reminders succeeded..")
    except FileNotFoundError:
        print(f"File 'reminders.txt' not found in current working directory: {os.getcwd()}")
        reminders = []

def hello_world1():
    load_reminders()
    print(f"Hello world1! The value of __name__ is: {__name__}")

@app.route('/')
def index():
    print("inside index..")
    print(reminders)
    hello_world1()
    print(reminders)
    return render_template('index3.html', reminders=reminders)



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
    load_reminders()
    app.run(debug=True,host='0.0.0.0', port=80)
