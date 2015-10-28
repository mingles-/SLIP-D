from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager

from Project import settings
import main

main.app.config.from_object(settings.Config)

migrate = Migrate(main.app, main.db)
manager = Manager(main.app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()