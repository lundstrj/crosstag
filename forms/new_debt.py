from flask.ext.wtf import Form
from wtforms import DecimalField, TextField, RadioField, DateField, validators, IntegerField



class NewDebt(Form):
    amount = IntegerField('amount', validators=[])
    product = TextField('product', [validators.Length(max=60)])
