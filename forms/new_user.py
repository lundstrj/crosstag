from flask.ext.wtf import Form
from wtforms import TextField, RadioField, DateField, validators


class NewUser(Form):
    name = TextField('name', [validators.Length(max=80), validators.DataRequired()])
    email = TextField('email', [validators.Length(max=120), validators.Email()])
    phone = TextField('phone', validators=[])
    address = TextField('address', [validators.Length(max=50), validators.DataRequired()])
    address2 = TextField('address2', [validators.Length(max=50)])
    city = TextField('city', [validators.Length(max=120), validators.DataRequired()])
    zip_code = TextField('zip_code', validators=[])
    tag_id = TextField('tag_id', validators=[])
    expiry_date = DateField('expiry_date', validators=[], format='%Y-%m-%d', description="DESC1")
    birth_date = DateField('birth_date', format='%Y-%m-%d', validators=[])
    gender = RadioField('gender', [validators.DataRequired()], choices=[('male', 'male'), ('female', 'female'),
                                                                        ('unknown', 'unknown')])