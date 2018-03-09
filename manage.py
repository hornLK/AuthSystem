import os

from app import create_app,db,mail
from app.models import (User,Role, Hosts,
                        HostGroup,AuthLog,
                        UserToHosts)
from flask_script import Manager,Shell
from flask_migrate import Migrate,MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app,db)

def make_shell_context():
    return dict(
        app = app,db = db,mail = mail,User = User,
        Role=Role,Hosts=Hosts,HostGroup=HostGroup,
        AuthLog=AuthLog,UserToHosts=UserToHosts)
manager.add_command("shell",
                    Shell(make_context=make_shell_context)
                   )
manager.add_command("db",
                   MigrateCommand
                   )

if __name__ == "__main__":
    manager.run()
