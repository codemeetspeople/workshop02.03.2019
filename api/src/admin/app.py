"""Synctool Admin Application module."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin

from config import settings
from admin.views import MODEL_VIEWS


app = Flask(__name__)
app.config.update(settings.admin)

db = SQLAlchemy(app)
db.init_app(app)

admin = Admin(app, url='/', name=settings.application, template_mode='bootstrap3')

for name, model_view in MODEL_VIEWS.items():
    admin.add_view(model_view(model_view.model, db.session))
