# (flask_1) C:\Users\user\Desktop\JJW\05. master course\수업\2024년 1학기\AI융합프로젝트\코드\flask-soft-ui-dashboard-master\flask-soft-ui-dashboard-master>python run.py
# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
from sys import exit

from flask_migrate import Migrate
from flask_minify import Minify

from api_generator.commands import gen_api
from apps import create_app, db
from apps.config import config_dict

# WARNING: Don't run with debug turned on in production!
DEBUG = (os.getenv('DEBUG', 'False') == 'True')

# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

try:

    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app(app_config)
Migrate(app, db)

if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)
    
if DEBUG:
    app.logger.info('DEBUG            = ' + str(DEBUG)             )
    app.logger.info('Page Compression = ' + 'FALSE' if DEBUG else 'TRUE' )
    app.logger.info('DBMS             = ' + app_config.SQLALCHEMY_DATABASE_URI)
    app.logger.info('ASSETS_ROOT      = ' + app_config.ASSETS_ROOT )

for command in [gen_api, ]:
    app.cli.add_command(command)
    
if __name__ == "__main__":
    app.run(host='0.0.0.0')
