from flask import jsonify
from datetime import datetime
from crosstag_init import db


class User(db.Model):
    index = db.Column(db.Integer, primary_key=True)
    fortnox_id = db.Column(db.Integer)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(50))
    address2 = db.Column(db.String(50))
    city = db.Column(db.String(120))
    zip_code = db.Column(db.Integer)
    tag_id = db.Column(db.String(20))
    gender = db.Column(db.String(10))
    ssn = db.Column(db.String(13))
    expiry_date = db.Column(db.Date)
    create_date = db.Column(db.Date)
    status = db.Column(db.String(50))
    tagcounter = db.Column(db.Integer)
    last_tag_timestamp = db.Column(db.DateTime)

    def __init__(self, name, email, phone=None, address=None, address2=None, city=None, zip_code=None, tag_id=None, fortnox_id=None,
                 expiry_date=None, ssn=None, gender=None, status=None, last_tag_timestamp=None):
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.address2 = address2
        self.city = city
        self.zip_code = zip_code
        self.tag_id = tag_id
        self.fortnox_id = fortnox_id
        self.expiry_date = expiry_date
        self.ssn = ssn
        self.gender = gender
        self.create_date = datetime.now()
        self.status = status
        if(self.tagcounter is None):
            self.tagcounter = 0


    def dict(self):
        return {'index': self.index, 'name': self.name,
                'email': self.email, 'tag_id': self.tag_id,
                'phone': self.phone, 'address': self.address,
                'address2': self.address2, 'city': self.city,
                'zip_code': self.zip_code,
                'tag_id': self.tag_id,
                'fortnox_id': self.fortnox_id,
                'expiry_date': str(self.expiry_date),
                'create_date': str(self.create_date),
                'ssn': self.ssn,
                'gender': self.gender,
                'status': self.status,
                'tagcounter': self.tagcounter,
                'last_tag_timestamp': self.last_tag_timestamp
                }

    def json(self):
        return jsonify(self.dict())
