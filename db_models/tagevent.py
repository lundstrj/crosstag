from flask import jsonify
from datetime import datetime
from crosstag_init import db
from db_models.user import User


class Tagevent(db.Model):
    tagid = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    amount = db.Column(db.Integer)
    clockstamp = db.Column(db.Integer)

    def __init__(self):
        self.timestamp = datetime.now()
        self.clockstamp = self.timestamp.hour


    def dict(self):
        return {'tagid': self.tagid, 'timestamp': str(self.timestamp), 'amount': self.amount, 'clockstamp': str(self.clockstamp)}

    def json(self):
        return jsonify(self.dict())
