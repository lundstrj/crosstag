from flask.ext.wtf import Form
from wtforms import DecimalField, StringField


class NewDebt(Form):
    amount = DecimalField('amount', validators=[])
    uid = StringField('uid', validators=[])