from flask import jsonify
from crosstag_init import db


class Debt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric)
    uid = db.Column(db.Integer)

    def __init__(self, amount=None, uid=None):
        self.amount = amount
        self.uid = uid

    def dict(self):
        return {'id': self.id, 'amount': self.amount, 'uid': self.uid}

    def json(self):
        return jsonify(self.dict())
