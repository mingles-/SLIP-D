import models
from flask.ext.security import SQLAlchemyUserDatastore, Security

# Setup Flask-Security
from Project.app import db, app

user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
security = Security(app, user_datastore)