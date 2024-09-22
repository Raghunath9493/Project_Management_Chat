# email_utils.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, content, to_email):
    HOST = "smtp-mail.outlook.com"
    PORT = 587
    FROM_EMAIL = ""  # Replace with your email address
    PASSWORD = ""

    # Create the email content
    message = MIMEMultipart()
    message['From'] = FROM_EMAIL
    message['To'] = to_email
    message['Subject'] = subject

    # Attach the email body
    message.attach(MIMEText(content, 'plain'))


 # Convert the message to a string and send it
    with smtplib.SMTP(HOST, PORT) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(FROM_EMAIL, PASSWORD)
        smtp.sendmail(FROM_EMAIL, to_email, message.as_string())

