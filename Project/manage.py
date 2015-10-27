from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager

from Project import settings
from app import app, db

app.config.from_object(settings.Config)

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()