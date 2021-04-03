import os

from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__, instance_relative_config=True)
# instance_relative_config let the app find configure file in relative folder

# make configuration
app.config.from_pyfile('config.py')

mail = Mail(app)

# ensure the instance path exists
try:
	os.makedirs(app.instance_path)
except OSError:
	pass

# register blueprints
import db
import auth
import main
from exmat import contract

db.register_with(app)
app.register_blueprint(main.bp)
app.register_blueprint(auth.bp)
app.register_blueprint(contract.bp)

	
if __name__ == "__main__":
	app.run(debug=True)
