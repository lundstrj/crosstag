from flask.ext.wtf import Form
from wtforms import TextField, RadioField, DateField
from wtforms.validators import Required


class EditUser(Form):
    name = TextField('name', validators=[])
    email = TextField('email', validators=[])
    phone = TextField('phone', validators=[])
    address = TextField('address', validators=[])
    address2 = TextField('address2', validators=[])
    city = TextField('city', validators=[])
    zip_code = TextField('zip_code', validators=[])
    tag_id = TextField('tag_id', validators=[])
    expiry_date = DateField('expiry_date', validators=[], format='%Y-%m-%d',
                            description="DESC1")
    birth_date = DateField('birth_date', format='%Y-%m-%d', validators=[])
    gender = RadioField(
        'gender',
        [Required()],
        choices=[('male', 'male'), ('female', 'female'),
                 ('unknown', 'unknown')])

    status = RadioField(
        'status',
        [Required()],
        choices=[('active', 'active'), ('inactive', 'inactive'), ('frozen', 'frozen'),
                 ('free', 'free'), ('special', 'special')]
    )