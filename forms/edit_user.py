from flask.ext.wtf import Form
from wtforms import TextField, RadioField, DateField, validators
from wtforms.validators import Required


class EditUser(Form):
    name = TextField('name', [validators.Length(max=80), validators.DataRequired()])
    email = TextField('email', [validators.Length(max=120), validators.Email()])
    phone = TextField('phone', validators=[])
    address = TextField('address', [validators.Length(max=50), validators.DataRequired()])
    address2 = TextField('address2', [validators.Length(max=50)])
    city = TextField('city', [validators.Length(max=120), validators.DataRequired()])
    zip_code = TextField('zip_code', validators=[])
    tag_id = TextField('tag_id', validators=[])
    expiry_date = DateField('expiry_date', [validators.Optional()], format='%Y-%m-%d', description="DESC1")
    gender = RadioField('gender', [validators.DataRequired()], choices=[('male', 'male'), ('female', 'female'),
                                                                      ('unknown', 'unknown')])
    status = RadioField(
        'status',
        [Required()],
        choices=[('Active', 'active'), ('Inactive', 'inactive'), ('Frozen', 'frozen'),
                 ('Free', 'free'), ('Special', 'special')]
    )