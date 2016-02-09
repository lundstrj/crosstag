# -*- coding: utf-8 -*-
from flask import Flask, jsonify, render_template, flash
import json
from generateStatistics import generateStats
from flask.ext.sqlalchemy import SQLAlchemy
from optparse import OptionParser
from flask.ext.wtf import Form
from wtforms import TextField, RadioField, DateField
from wtforms.validators import Required
from datetime import datetime, timedelta

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
app_name = 'crosstag'


class NewTag(Form):
    tag_id = TextField('tag_id', validators=[])


class NewUser(Form):
    name = TextField('name', validators=[])
    email = TextField('email', validators=[])
    phone = TextField('phone', validators=[])
    fortnox_id = TextField('fortnox_id', validators=[])
    tag_id = TextField('tag_id', validators=[])
    expiry_date = DateField('expiry_date', validators=[], format='%Y-%m-%d',
                            description="DESC1")
    birth_date = DateField('birth_date', format='%Y-%m-%d', validators=[])
    gender = RadioField(
        'gender',
        [Required()],
        choices=[('male', 'male'), ('female', 'female'),
                 ('unknown', 'unknown')], default='unknown'
    )


class SearchUser(Form):
    index = TextField('name', validators=[])
    name = TextField('name', validators=[])
    email = TextField('email', validators=[])
    phone = TextField('phone', validators=[])
    fortnox_id = TextField('fortnox_id', validators=[])
    tag = TextField('tag', validators=[])
    gender = RadioField(
        'gender',
        [Required()],
        choices=[('male', 'male'), ('female', 'female'),
                 ('unknown', 'unknown')], default='unknown'
    )


class EditUser(Form):
    name = TextField('name', validators=[])
    email = TextField('email', validators=[])
    phone = TextField('phone', validators=[])
    fortnox_id = TextField('fortnox_id', validators=[])
    tag_id = TextField('tag_id', validators=[])
    expiry_date = DateField('expiry_date', validators=[], format='%Y-%m-%d',
                            description="DESC1")
    birth_date = DateField('birth_date', format='%Y-%m-%d', validators=[])
    create_date = DateField('create_date', format='%Y-%m-%d', validators=[])
    gender = RadioField(
        'gender',
        [Required()],
        choices=[('male', 'male'), ('female', 'female'),
                 ('unknown', 'unknown')]
    )


class User(db.Model):
    index = db.Column(db.Integer, primary_key=True)
    fortnox_id = db.Column(db.Integer)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120))
    phone = db.Column(db.Integer)
    tag_id = db.Column(db.String(12))
    gender = db.Column(db.String(10))
    birth_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    create_date = db.Column(db.Date)

    def __init__(self, name, email, phone=None, tag_id=None, fortnox_id=None,
                 expiry_date=None, birth_date=None, gender=None):
        self.name = name
        self.email = email
        self.phone = phone
        self.tag_id = tag_id
        self.fortnox_id = fortnox_id
        self.expiry_date = expiry_date
        self.birth_date = birth_date
        self.gender = gender
        self.create_date = datetime.now()

    def dict(self):
        return {'index': self.index, 'name': self.name,
                'email': self.email, 'tag_id': self.tag_id,
                'phone': self.phone, 'fortnox_id': self.fortnox_id,
                'expiry_date': str(self.expiry_date),
                'create_date': str(self.create_date),
                'birth_date': str(self.birth_date),
                'gender': self.gender}

    def json(self):
        return jsonify(self.dict())


class Tagevent(db.Model):
    index = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime)
    uid = db.Column(db.Integer, db.ForeignKey('user.index'))

    def __init__(self, tag):
        self.tag_id = tag
        self.timestamp = datetime.now()
        users = User.query.filter_by(tag_id=self.tag_id)
        js = None
        for user in users:
            js = user.dict()

        self.uid = js['index']


    def dict(self):
        return {'index': self.index, 'timestamp': str(self.timestamp),
                'tag_id': self.tag_id, 'uid':self.uid}

    def json(self):
        return jsonify(self.dict())


def get_last_tag_event():
    top_index = db.session.query(db.func.max(Tagevent.index)).scalar()
    tagevent = Tagevent.query.filter_by(index=top_index).first()
    return tagevent


@app.route('/')
@app.route('/index')
@app.route('/%s' % app_name)
def index():
    return render_template('index.html')


@app.route('/crosstag/v1.0/tagevent/<tag_id>')
def tagevent(tag_id):
    event = Tagevent(tag_id)
    db.session.add(event)
    db.session.commit()
    return "%s server tagged %s" % (event.timestamp, tag_id)


@app.route('/crosstag/v1.0/last_tagin', methods=['GET'])
def last_tagin():
    try:
        return Tagevent.query.all()[-1].json()
    except:
        return jsonify({})


@app.route('/crosstag/v1.0/get_user_data_tag/<tag_id>', methods=['GET'])
def get_user_data_tag(tag_id):
    try:
        return User.query.filter_by(tag_id=tag_id).first().json()
    except:
        return jsonify({})


@app.route('/crosstag/v1.0/specialtagevent/<tag_id>/<timestamp>')
def specialtagevent(tag_id, timestamp):
    event = Tagevent(tag_id)
    # date_object = datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')
    event.timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M')
    db.session.add(event)
    db.session.commit()
    return "%s server tagged %s" % (event.timestamp, tag_id)


@app.route('/all_tagevents', methods=['GET'])
def all_tagevents():
    ret = []
    events = Tagevent.query.all()
    for hit in events:
        js = hit.dict()
        ret.append(js)
    ret.reverse()
    return render_template('all_tagevents.html',
                           title='All Tagevents',
                           hits=ret)


@app.route('/all_users', methods=['GET'])
def all_users():
    ret = []
    users = User.query.all()
    for hit in users:
        js = hit.dict()
        ret.append(js)
    return render_template('all_users.html',
                           title='All Users',
                           hits=ret)


@app.route('/crosstag/v1.0/get_user_data_tag_dict/<tag_id>',
           methods=['GET'])
def get_user_data_tag_dict(tag_id):
    user = User.query.filter_by(tag_id=tag_id).first()
    return user.dict()


@app.route('/last_tagins', methods=['GET'])
def last_tagins():
    ret = []
    events = Tagevent.query.all()[-10:]
    for hit in events:
        js = hit.dict()
        tag = js['tag_id']
        try:
            user = get_user_data_tag_dict(tag)
            js['user_index'] = user["index"]
            js['user_name'] = user['name']
        except:
            js['user_index'] = None
            js['user_name'] = "No user connected to this tag"
        ret.append(js)
    ret.reverse()
    return render_template('last_tagevents.html',
                           title='Last Tagins',
                           hits=ret)


@app.route('/crosstag/v1.0/remove_user/<index>', methods=['POST'])
def remove_user(index):
        user = User.query.filter_by(index=index).first()
        db.session.delete(user)
        db.session.commit()
        return "removed user"


@app.route('/add_new_user', methods=['GET', 'POST'])
def add_new_user():
    form = NewUser()
    print("errors", form.errors)
    if form.validate_on_submit():
        tmp_usr = User(form.name.data, form.email.data, form.phone.data,
                       form.tag_id.data, form.fortnox_id.data,
                       form.expiry_date.data, form.birth_date.data,
                       form.gender.data)
        db.session.add(tmp_usr)
        db.session.commit()
        flash('Created new user: %s with id: %s' % (form.name.data,
                                                    tmp_usr.index))
        tagevent = get_last_tag_event()
        msg = None
        if tagevent is None:
            msg = None
        else:
            msg = (tmp_usr.index, tagevent.tag_id)
        form = NewUser()
        return render_template('new_user.html',
                               title='New User',
                               form=form,
                               message=msg)
    return render_template('new_user.html',
                           title='New User',
                           form=form)


@app.route('/tagin_user', methods=['GET', 'POST'])
def tagin_user():
    form = NewTag(csrf_enabled=False)

    print(str(form.validate_on_submit()))
    print("errors", form.errors)
    if form.validate_on_submit():
        tmp_tag = Tagevent(form.tag_id.data)

        db.session.add(tmp_tag)
        db.session.commit()
        flash('New tag created')
        return render_template('tagin_user.html',
                               title='New tag',
                               form=form)
    return render_template('tagin_user.html',
                               title='New tag',
                               form=form)

@app.route('/search_user', methods=['GET', 'POST'])
def search_user():
    form = SearchUser()
    print(str(form.validate_on_submit()))
    print("errors", form.errors)
    hits = []
    if form.validate_on_submit():
        if form.index.data:
            user_index = form.index.data
            users = User.query.filter_by(index=user_index)
            hits.extend(users)
        if form.fortnox_id.data:
            fortnox_id = form.fortnox_id.data
            users = User.query.filter_by(fortnox_id=fortnox_id)
            hits.extend(users)
        if form.name.data:
            name = form.name.data
            users = User.query.filter(User.name.ilike('%' + name + '%'))
            hits.extend(users)
        if form.email.data:
            email = form.email.data
            users = User.query.filter_by(email=email)
            hits.extend(users)
        if form.phone.data:
            phone = form.phone.data
            users = User.query.filter_by(phone=phone)
            hits.extend(users)
        if form.tag.data:
            tag = form.tag.data
            users = User.query.filter_by(tag=tag)
            hits.extend(users)
        ret = []
        for hit in hits:
            js = hit.dict()
            ret.append(js)
        return render_template('search_user.html',
                               title='Search User',
                               form=form,
                               hits=ret)
    return render_template('search_user.html',
                           title='Search User',
                           form=form)


@app.route('/crosstag/v1.0/link_user_to_last_tag/<user_id>',
           methods=['GET', 'POST'])
def link_user_to_last_tag(user_id):
    tagevent = get_last_tag_event()
    user = User.query.filter_by(index=user_id).first()
    user.tag_id = tagevent.tag_id
    db.session.commit()
    return "OK"


@app.route('/crosstag/v1.0/get_tag/<user_index>', methods=['GET'])
def get_tag(user_index):
    user = User.query.filter_by(index=user_index).first()
    return str(user.tag_id)


@app.route('/crosstag/v1.0/get_tagevents_user_dict/<user_index>',
           methods=['GET'])
def get_tagevents_user_dict(user_index):
    tag_id = get_tag(user_index)
    events = Tagevent.query.filter_by(tag_id=tag_id)[-20:]
    ret = []
    for hit in events:
        js = hit.dict()
        ret.append(js)
    ret.reverse()
    return ret


@app.route('/statistics', methods=['GET'])
def statistics():

    gs = generateStats()

    # Fetch the data from the database.
    users = User.query.all()
    event = Tagevent

    # Send the data to a method who returns an multi dimensional array with statistics.
    ret = gs.get_data(users, event)

    return render_template('statistics.html',
                           plot_paths='',
                           data=ret)


class Exercise(db.Model):
    index = db.Column(db.Integer, primary_key=True)
    exercise = db.Column(db.String(20))

    def __init__(self):
        self.exercise = None

    def dict(self):
        return {'index': self.index, 'exercise': self.exercise}

    def json(self):
        return jsonify(self.dict())


# TEST KLASS!!!!!---------------------------------------------------------------------------------------
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
        return {'id': self.id, 'exercise_id': self.exercise_id, 'record': self.record, 'unit': self.unit, 'record_date': self.record_date, 'uid':self.uid}

    def json(self):
        return jsonify(self.dict())


# TEST FUNKTION!!!!!
@app.route('/pb/<user_id>', methods=['GET'])
def pb(user_id):

### OLD SHIT, Save for future reference--------------------------------|
    #tag_id = get_tag(1)
    #events = Statistics.query.filter_by(tag_id=tag_id)[-20:]
    #userList = users.query.join(friendships, users.id==friendships.user_id)
    # .add_columns(users.userId, users.name, users.email, friends.userId, friendId)
    # .filter(users.id == friendships.friend_id).filter(friendships.user_id == userID).paginate(page, 1, False)

    '''results = User.query.join(Statistics, User.index == Statistics.uid).add_columns(User.name, User.tag_id, Statistics.exercise, Statistics.record, Statistics.unit, Statistics.record_date, Statistics.uid).filter(User.index == user_id).filter(Statistics.uid == user_id)
    ret = []
    logging.debug("hello")'''
### END OF OLD SHIT----------------------------------------------------|


    users = User.query.filter_by(index=user_id)
    personalstats = Records.query.filter_by(uid=user_id)


    ret = []
    userret = []
    exerciseret = []

    #name = User.name
    for hit in personalstats:
        pbjs = hit.dict()
        ret.append(pbjs)

   #  exercise = Exercise.query.filter_by(index=pbjs['exercise_id'])
    #exercisejs = exercise[0].dict()
    #exerciseret.append(exercisejs)

    for hit in users:
        js = hit.dict()
        userret.append(js)

   # ret.append(name)
    return render_template('PB.html', plot_paths='', data=ret, users=userret, exercises=exerciseret)

   # return render_template('PB.html', plot_paths='', data=ret, users=userret, exercisetypes=exercisearr)
#-----------------------------------------------------------------------------------------------------


@app.route('/getrecenteventsgender', methods=['GET'])
def get_recent_events_gender():
    three_months_ago = datetime.now() - timedelta(weeks=8)
    events = Tagevent.query.filter(Tagevent.timestamp>three_months_ago).all()
    
    events_json={}
    genders = []

    for event in events:
        current=str(event.timestamp.date())
        try:
            gender=User.query.filter_by(tag_id=event.tag_id).first().gender
        except: 
            gender='unknown'
        
        genders.append(gender)

        if current in events_json:
            events_json[current] += 1
        else:
            events_json[current] = 1
    
   #[{datestamp: ["2014-12-22", "2014-12-23"], unknown: [0,0], male: [9, 5], female: [0,0]}]
    res = [{'datestamp': male.keys(), 'male': male.values(), 'female': female.values(), 'unknown': unknown.values()} ]
    return json.dumps(res)


@app.route('/getrecentevents', methods=['GET'])
def get_recent_events():
    three_months_ago = datetime.now() - timedelta(weeks=8)
    tags = Tagevent.query.filter(Tagevent.timestamp > three_months_ago).all()
    tags_json = {}

    for tag in tags:
        current = str(tag.timestamp.date())
        if current in tags_json:
            tags_json[current] += 1
        else:
            tags_json[current] = 1

    # add zeroes to all the unvisited days
    tmp_date = three_months_ago.date()
    while tmp_date < datetime.now().date():
        if str(tmp_date) in tags_json:
            pass
        else:
            tags_json[str(tmp_date)] = 0
        tmp_date = tmp_date + timedelta(days=1)

    res = [{'datestamp': x, 'count': y} for x, y in tags_json.iteritems()]
    return json.dumps(res)


@app.route('/edit_user/<user_index>', methods=['GET', 'POST'])
def edit_user(user_index=None):
    user = User.query.filter_by(index=user_index).first()
    if user is None:
        return "she wrote upon it; no such number, no such zone"
    form = EditUser(obj=user)
    tagevents = get_tagevents_user_dict(user_index)

    if form.validate_on_submit():
        user.fortnox_id = form.fortnox_id.data
        user.name = form.name.data
        user.email = form.email.data
        user.phone = form.phone.data
        user.tag_id = form.tag_id.data
        user.gender = form.gender.data
        user.birth_date = form.birth_date.data
        user.expiry_date = form.expiry_date.data
        user.create_date = form.create_date.data
        db.session.commit()
        flash('Updated user: %s with id: %s' % (form.name.data, user.index))
        tagevent = get_last_tag_event()
        msg = None
        if tagevent is None:
            msg = None
        else:
            msg = (user.index, tagevent.tag_id)
        user = User.query.filter_by(index=user_index).first()
        return render_template('edit_user.html',
                               title='Edit User',
                               form=form,
                               data=user.dict(),
                               message=msg,
                               tags=tagevents)
    if user:
        return render_template('edit_user.html',
                               title='Edit User',
                               form=form,
                               data=user.dict(),
                               tags=tagevents)
    else:
        return "she wrote upon it; no such number, no such zone"


@app.route('/%s/v1.0/link_user_to_tag/<user_index>/<tag_id>' % app_name,
           methods=['POST'])
def link_user_to_tag(user_index, tag_id):
    user = User.query.filter_by(index=user_index).first()
    user.tag = tag_id
    db.session.commit()
    return "OK"


@app.route('/%s/v1.0/get_all_users' % app_name, methods=['GET'])
def get_all_users():
    users = User.query.all()
    ret = {}
    for user in users:
        ret[user.index] = {}
        ret[user.index]['name'] = user.name
        ret[user.index]['tag'] = user.tag_id
    ret = jsonify(ret)
    return ret


if __name__ == '__main__':
    parser = OptionParser(usage="usage: %prog [options] arg \nTry this: " +
                          "python crosstag_server.py", version="%prog 1.0")
    parser.add_option('--debug', dest='debug', default=False, action='store_true', help="Do you want to run this thing with debug output?")
    (options, args) = parser.parse_args()
    #config['database_file'] = options.database
    #config['secret_key'] = options.secret
    db.create_all()
    #if options.debug:
    app.logger.propagate = False
    app.run(host='0.0.0.0', port=app.config["PORT"], debug=True)


