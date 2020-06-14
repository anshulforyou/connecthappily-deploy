import smtplib
from email.mime.text import MIMEText

def send_mail(name, email, phone, feedback_for, feedback):
    port = 2525
    smtp_server = 'smtp.mailtrap.io'
    login = 'ec778797fc261e'
    password = '0dcaf0d1565ca6'
    message = f'<h3>New Feedback Submission</h3><ul><li>Name:{name}</l><li>Phone:{phone}</l><li>Email:{email}</l><li>Feedback for:{feedback_for}</l><li>Feedback:{feedback}</l></ul></h3>'

    sender_email = 'doesntmatter@example.com'
    receiver_email = 'doesntmatter2@example2.com'
    msg = MIMEText(message, 'html')
    msg['Subject'] = "Connect Happily Stage 1 web platform feedback"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    with smtplib.SMTP(smtp_server, port) as server:
        server.login(login, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())