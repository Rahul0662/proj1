import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(sender_email, receiver_email, subject, message, smtp_server, smtp_port, smtp_user, smtp_password):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    body = message
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        print("Email sent successfully!")
    except Exception as e:
        print("Failed to send email:", str(e))
    finally:
        server.quit()

# Example usage:
sender_email = "abc@xyz.com"
receiver_email = "recipient@example.com"
subject = "Test Email"
message = "This is a test email sent using Python SMTP."
smtp_server = "smtpauth.iis.xyz.net"
smtp_port = 25
smtp_user = "app-user1"
smtp_password = "p@ssword"

send_email(sender_email, receiver_email, subject, message, smtp_server, smtp_port, smtp_user, smtp_password)
