from flask.ext.wtf import Form
from wtforms import TextField


class NewTag(Form):
    tag_id = TextField('tag_id', validators=[])