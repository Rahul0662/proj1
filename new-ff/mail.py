from flask import Flask, render_template
from flask_mail import Mail, Message

app = Flask(__name__)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'your_smtp_server'  # Replace with your SMTP server address
app.config['MAIL_PORT'] = 587  # Port for TLS encryption (common for Gmail)
app.config['MAIL_USE_TLS'] = True  # Enable TLS encryption
app.config['MAIL_USERNAME'] = 'your_email@example.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'your_password'  # Replace with your email password

mail = Mail(app)

@app.route('/')
def send_email():
    msg = Message('Test Email from Flask App', sender='your_email@example.com', recipients=['recipient_email@example.com'])
    msg.body = "This is a test email sent from a Flask application."
    msg.html = render_template('email.html', content="This is a test email with HTML content.")  # Optional HTML content

    try:
        mail.send(msg)
        return "Email sent successfully!"
    except Exception as e:
        return f"Error sending email: {e}"

if __name__ == '__main__':
    app.run(debug=True)
