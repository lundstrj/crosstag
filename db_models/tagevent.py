from flask import jsonify
from datetime import datetime
from crosstag_server import db
from db_models.user import User


class Tagevent(db.Model):
    index = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime)
    uid = db.Column(db.Integer, db.ForeignKey('user.index'))

    def __init__(self, tag):
        self.tag_id = tag
        self.timestamp = datetime.now()
        users = User.query.filter_by(tag_id=self.tag_id)
        js = None
        for user in users:
            js = user.dict()

        # Vi får ut tag id så att man enklare kan lägga till det på en ny medlem!
        if js is not None:
            self.uid = js['index']

    def dict(self):
        return {'index': self.index, 'timestamp': str(self.timestamp),
                'tag_id': self.tag_id, 'uid': self.uid}

    def json(self):
        return jsonify(self.dict())
