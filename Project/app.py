import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from Project import settings

app = Flask(__name__)

import logging
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

app.config.from_object(settings.TestingConfig)

db = SQLAlchemy(app)
