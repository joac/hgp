#! -*- coding: utf8 -*-

from flask.ext.wtf import (
        FileField,
        Form,
        IntegerField,
        SelectField,
        TextAreaField,
        TextField,
        validators,
        )

#FIXME Write custom field for tag handling
#FIXME Validation of url


class BaseForm(Form):
    name = TextField(u'Name', [validators.required()])
    description = TextAreaField(u'Description')
    weight = IntegerField(u'Image weight')
    tags = TextField(u'Tags')


class PhotoForm(BaseForm):
    image = FileField(u'Image File')

class VideoForm(BaseForm):
    source = SelectField(u'Source', choices=[('youtube', 'Youtube'), ('vimeo', 'Vimeo')])
    url = TextField(u'Url', [validators.required()])
