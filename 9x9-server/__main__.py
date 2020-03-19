import os
import configparser
import pathlib

from .server import Server

config_path = pathlib.Path(__file__).parent.parent
def get_config_path(name):
    return config_path.joinpath(name).absolute()
config = configparser.ConfigParser()
config.read([get_config_path(name) for name in ('9x9-server-default.conf', '9x9-server.conf')])

PORT = config['9x9-server'].getint('PORT')
print(f'Starting 9x9-server at {PORT}...')
srv = Server(PORT)
srv.start()
