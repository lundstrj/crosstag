from flask import jsonify
from datetime import datetime
from crosstag_init import db


class Debt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    uid = db.Column(db.Integer)
    product = db.Column(db.VARCHAR(60))
    create_date = db.Column(db.Date)

    def __init__(self, amount=None, uid=None, product=None, create_date=None):
        self.amount = amount
        self.uid = uid
        self.product = product
        self.create_date = datetime.now()

    def dict(self):
        return {'id': self.id,
                'amount': self.amount,
                'uid': self.uid,
                'product': self.product,
                'create_date': str(self.create_date)}

    def json(self):
        return jsonify(self.dict())
