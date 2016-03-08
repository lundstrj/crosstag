from flask.ext.wtf import Form
from wtforms import TextField


class SearchUser(Form):
    index = TextField('name', validators=[])
    name = TextField('name', validators=[])
    email = TextField('email', validators=[])
    phone = TextField('phone', validators=[])
    fortnox_id = TextField('fortnox_id', validators=[])
