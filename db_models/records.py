from flask import jsonify
from datetime import datetime
from crosstag_server import db


class Records(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.index'))
    record = db.Column(db.Float)
    unit = db.Column(db.String(10))
    record_date = db.Column(db.Date)
    uid = db.Column(db.Integer, db.ForeignKey('user.index'))

    def __init__(self):
        self.exercise_id = None
        self.record = None
        self.unit = None
        self.record_date = datetime.now()

    def dict(self):
        return {'id': self.id, 'exercise_id': self.exercise_id, 'record': self.record, 'unit': self.unit,
                'record_date': self.record_date, 'uid': self.uid}

    def json(self):
        return jsonify(self.dict())
