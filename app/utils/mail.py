import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from flask import current_app, url_for
from utils import safe
from utils import data_signature

def send_email_confirmation(to):
	tm = datetime.today().strftime("%Y%m%d%H%M%S")
	sig = data_signature.sign(bytes(to + tm + 'ec', "utf-8"))
	url = url_for("auth.email_confirmation") + safe.parse_args({
		"email":to, "time":tm, "sig":sig
	})
	
	return url
	# Create the plain-text and HTML version of your message
	with current_app.open_resource('confirmation.md') as f:
		text = f.read().decode('utf-8').format(url=url)
	with current_app.open_resource('confirmation.html') as f:
		html = f.read().decode('utf-8').format(url=url)
		
	# Turn these into plain/html MIMEText objects
	part1 = MIMEText(text, "plain")
	part2 = MIMEText(html, "html")
	
	message = MIMEMultipart("alternative")
	message["Subject"] = "Email Confirmation"
	message["From"] = current_app.config['MAIL_DEFAULT_SENDER']
	message["To"] = to
	
	# Add HTML/plain-text parts to MIMEMultipart message
	# The email client will try to render the last part first
	message.attach(part1)
	message.attach(part2)

	sender_email = current_app.config['MAIL_USERNAME']
	password = current_app.config['MAIL_PASSWORD']

	# Create secure connection with server and send email
	context = ssl.create_default_context()
	with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
		server.login(sender_email, password)
		server.sendmail(
        	sender_email, receiver_email, message.as_string()
    	)

def send_password_confirmation(to):
	tm = datetime.today().strftime("%Y%m%d%H%M%S")
	sig = data_signature.sign(bytes(to + tm + 'pc', "utf-8"))
	url = url_for("auth.email_confirmation") + safe.parse_args({
		"email":to, "time":tm, "sig":sig
	})
	
	return url

def send_email_confirmation_code(email, code):
    pass