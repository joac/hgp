#! -*- coding: utf8 -*-

import inspect
import os
import app
import models

def create_tables():

    app.auth.User.create_table()

    def valid_model(c):
        return inspect.isclass(c) and issubclass(c, models.db.Model)

    for name, _class in [(n, c) for n, c in inspect.getmembers(models) if valid_model(c)]:
        _class.create_table()

    admin = app.auth.User(username='admin', admin=True, active=True, email='test@test.com')
    admin.set_password('admin')
    admin.save()

if __name__ == '__main__':
    create_tables()
