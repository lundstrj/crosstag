from flask import jsonify
from crosstag_init import db


class Debt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric)
    name = db.Column(db.String(50))

    def __init__(self, amount=None, name=None):
        self.amount = amount
        self.name = name

    def dict(self):
        return {'id': self.id, 'amount': self.amount, 'name': self.name}

    def json(self):
        return jsonify(self.dict())
