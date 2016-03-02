from flask import jsonify
from crosstag_server import db


class Exercise(db.Model):
    index = db.Column(db.Integer, primary_key=True)
    exercise = db.Column(db.String(20))

    def __init__(self):
        self.exercise = None

    def dict(self):
        return {'index': self.index, 'exercise': self.exercise}

    def json(self):
        return jsonify(self.dict())
