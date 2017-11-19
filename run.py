from flask import Flask
from drumbot.drumbot import mod

app = Flask(__name__)
app.register_blueprint(mod, url_prefix='')

if __name__ == '__main__':
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.debug = True
