# -*- coding: utf-8 -*-
import os

from flask import Flask
from flask_session import Session

from redis import Redis

import codecs
import json


app = Flask(__name__)

config_filename = os.getenv("FLASK_CONFIGFILE", "config.live.json")

with codecs.open(config_filename, "r", "utf-8") as config_file:
    config = json.loads(config_file.read())
    app.config.update(**config['flask'])

redis = Redis(config['redis']['host'])
app.config.update(SESSION_REDIS=redis)

Session(app)

from views.test_views import *

if __name__ == "__main__":
    import ssl

    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.load_cert_chain(config['secrets']['testing_ssl_cert'], config['secrets']['testing_ssl_key'])
    app.run(debug=True, host='0.0.0.0', port=config['app']['port'], ssl_context=context)