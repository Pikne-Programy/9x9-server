import os
import configparser
import pathlib

from .server import Server

config_path = pathlib.Path(__file__).parent.parent
def get_repo_path(name):
    return config_path.joinpath(name).absolute()
config = configparser.ConfigParser(allow_no_value=True)
config.read([get_repo_path(name) for name in ('9x9-server-default.conf', '9x9-server.conf')])

PORT = config['9x9-server'].getint('PORT')
THE_SECRET_COMMAND_UPDATING = config['9x9-server'].get('THE SECRET COMMAND UPDATING')
PING_EVERY = config['9x9-server'].getint('PING_EVERY')
print(f'Starting 9x9-server at {PORT}...')
print(f"The updating command is {'on' if THE_SECRET_COMMAND_UPDATING else 'off'}.")
print(f'Pinging every {PING_EVERY} seconds.')
srv = Server(PORT, updating_command=THE_SECRET_COMMAND_UPDATING, update_cmd='sudo /bin/systemctl start server9x9updater.service'.split(' '), ping_every=PING_EVERY)
srv.start()
