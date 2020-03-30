import subprocess

NAME = '9x9-server'
AUTHOR = 'Pikne-Programy'
LINK = f'https://github.com/{AUTHOR}/{NAME}/'
VERSION = subprocess.check_output('git describe --always --long --dirty'.split()).strip().decode()
PROTOCOL_VERSION = 'v1.0'
