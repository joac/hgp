# -*- coding: utf-8 -*-

TEMPLATE_VARIABLES = {
    'META': {
        'description': 'Hernan Pepe Portfolio',
        'keywords': 'Hernan, Pepe, Fotografia, condor, Photo',
        'author': 'Hernan Pepe',
    },
    'TITLE': ' | Hernan Pepe Photo',
    'LOGO': 'logo.png',
    'TAGS': (
        {'name': 'portfolio', 'display_name': 'PORTFOLIO'},
        {'name': 'condor', 'display_name': 'CONDOR ANDINO'},
        {'name': 'vintage', 'display_name': 'VINTAGE'},
        {'name': 'press', 'display_name': 'PRENSA'},
        {'name': 'contact', 'display_name': 'CONTACTO'},
    ),
    'GOOGLE_SITE_VERIFICATION': '9_6OmCLHS2ZSElRuH_eUAMjuRUJ-Fa95Du0osbb8WvQ',
}

UPLOAD_FOLDER = '/home/humitos/development/hgp/hgp/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'psd'])

DEBUG = True
SECRET_KEY = 'development key1'
USERNAME = 'admin'
PASSWORD = 'default'

# Override the above settings
from local_settings import *
