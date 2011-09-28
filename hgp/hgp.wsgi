import sys

sys.path.append('/var/www/hernanpepe.com.ar/web/hgp/hgp')
activate_this = '/var/www/hernanpepe.com.ar/web/hgp/env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
from hgp import app as application
