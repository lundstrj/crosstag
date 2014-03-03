from flask import Flask
from flask import jsonify
from flask import request
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime
from sqlalchemy.sql import text
from flask import make_response
from flask import render_template
from flask.ext.wtf import Form
from wtforms import TextField, BooleanField
from wtforms.validators import Required
from flask import render_template, flash, redirect
#from app import app
#from forms import LoginForm

"""
sudo pip install flask-security flask-sqlalchemy
sudo pip install Flask-WTF

"""

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/crosstag/crosstag.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///Users/lujo/dev/crosstag/crosstag_1.db'
app.config['WTF_CSRF_ENABLED'] = False
app.config['SECRET_KEY'] = 'foo'
db = SQLAlchemy(app)



class NewUser(Form):
    name = TextField('name', validators = [Required()])
    email = TextField('email', validators = [])
    phone = TextField('phone', validators = [])
    box_id = TextField('box_id', validators = [])
    tag = TextField('tag', validators = [])

class SearchUser(Form):
    id = TextField('id', validators = [])
    box_id = TextField('bo_id', validators = [])
    name = TextField('name', validators = [])
    email = TextField('email', validators = [])
    phone = TextField('phone', validators = [])
    tag = TextField('tag', validators = [])


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    box_id = db.Column(db.Integer)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120))
    phone = db.Column(db.Integer)
    tag = db.Column(db.String(12))

    def __init__(self, name, email, phone=None, tag=None, box_id=None):
        self.name = name
        self.email = email
        self.phone = phone
        self.tag = tag
        self.box_id = box_id

    def __repr__(self):
        return '<User %r>' % self.name
    
    def dict(self):
        return {'id':self.id, 'name':self.name, 'email':self.email, 'tag':self.tag, 'phone':self.phone, 'box_id':self.box_id}

    def json(self):
        d = jsonify({'id':self.id, 'name':self.name, 'email':self.email, 'tag':self.tag, 'phone':self.phone, 'box_id':self.box_id})
        return d

class Tagevent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime)
    tag = db.Column(db.Integer)

    def __init__(self, tag):
        self.tag = tag
        self.timestamp = datetime.now()
        #self.timestamp = 12345

    def dict(self):
        return {'id':self.id, 'timestamp':self.timestamp, 'tag':self.tag}

    def __str__(self):
        return '<Tagevent %s %s>' % (self.tag, self.timestamp)

    def __repr__(self):
        return '<Tagevent %s %s>' % (self.tag, self.timestamp)


def json_events(tag_id=None):
    if tag_id:
        events = Tagevent.query.filter_by(tag=tag_id)
    else:
        events = Tagevent.query.all()
    ret = {}
    for event in events:
        tmp = {}
        ret[event.id] = {}
        ret[event.id]['tag'] = event.tag
        ret[event.id]['timestamp'] = event.timestamp
    ret = jsonify(ret)
    return ret

def get_last_tag_event():
    res = db.engine.execute(text("SELECT max(id) FROM tagevent;"))
    row = res.fetchone()
    event_id = row[0]
    tagevent = Tagevent.query.filter_by(id=event_id).first()
    return tagevent

base_url = "/crosstag/v1.0/"

@app.route('/')
@app.route('/index')
@app.route('/crosstag')
def index():
    return render_template('index.html')

@app.route('/crosstag/v1.0/register_tag/<user_id>/<tag_id>')
def register_tag(user_id, tag_id):
    user = User.query.filter_by(id=user_id).first()
    user.tag = tag_id
    db.session.commit()
    return "OK"

@app.route('/crosstag/v1.0/link_user_to_last_tag/<user_id>', methods=['GET','POST'])
def link_user_to_last_tag(user_id):
    tagevent = get_last_tag_event()
    user = User.query.filter_by(id=user_id).first()
    user.tag = tagevent.tag
    db.session.commit()
    return "OK"

@app.route('/crosstag/v1.0/get_all_tagevents', methods = ['GET'])
def get_all_tagevents():
    return json_events()

@app.route('/crosstag/v1.0/get_all_users', methods = ['GET'])
def get_all_users():
    print "GET ALL THE USERS!"
    users = User.query.all()
    ret = {}
    for user in users:
        tmp = {}
        ret[user.id] = {}
        ret[user.id]['name'] = user.name
        ret[user.id]['tag'] = user.tag
    ret = jsonify(ret)
    return ret

@app.route('/crosstag/v1.0/get_tag/<user_id>', methods = ['GET'])
def get_tag(user_id):
    user = User.query.filter_by(id=user_id).first()
    return str(user.tag)

@app.route('/crosstag/v1.0/get_tagevents_user/<user_id>', methods = ['GET'])
def get_tagevents_user(user_id):
    tag_id = get_tag(user_id)
    return json_events(int(tag_id))

@app.route('/crosstag/v1.0/get_tagevents_user_dict/<user_id>', methods = ['GET'])
def get_tagevents_user_dict(user_id):
    tag_id = get_tag(user_id)
    events = Tagevent.query.filter_by(tag=tag_id)[-20:]
    ret = []
    for hit in events:
        js = hit.dict()
        ret.append(js)
    ret.reverse()
    return ret

@app.route('/crosstag/v1.0/get_tagevents_tag/<tag_id>', methods = ['GET'])
def get_tagevents_tag(tag_id):
    return json_events(tag_id)

@app.route('/crosstag/v1.0/get_user_data/<user_id>', methods = ['GET'])
def get_user_data(tag_id):
    user = User.query.filter_by(id=user_id).first()
    return user.json()

@app.route('/crosstag/v1.0/get_user_data_tag/<tag_id>', methods = ['GET'])
def get_user_data_tag(tag_id):
    try:
        user = User.query.filter_by(tag=tag_id).first()
        return user.json()
    except:
        return jsonify({})

@app.route('/crosstag/v1.0/get_user_data_tag_dict/<tag_id>', methods = ['GET'])
def get_user_data_tag_dict(tag_id):
    user = User.query.filter_by(tag=tag_id).first()
    return user.dict()

@app.route('/crosstag/v1.0/remove_user/<id>', methods = ['GET', 'POST'])
def remove_user(id):
        user = User.query.filter_by(id=id).first()
        db.session.delete(user)
        db.session.commit()
        return "removed user"

@app.route('/crosstag/v1.0/create_user/<name>/<email>/<phone>/<box_id>')
def create_user(name, email, phone, box_id):
        tmp_usr = User(name, email, phone, box_id=box_id)
        db.session.add(tmp_usr)
        db.session.commit()
        return "Created new user"

@app.route('/crosstag/v1.0/tagevent/<tag_id>')
def tagevent(tag_id):
    event = Tagevent(tag_id)
    db.session.add(event)
    db.session.commit()
    return "%s server tagged %s" % (event.timestamp, tag_id)

@app.route('/add_new_user', methods = ['GET', 'POST'])
def add_new_user():
    form = NewUser()
    if form.validate_on_submit():
        tmp_usr = User(form.name.data, form.email.data, form.phone.data, form.tag.data)
        db.session.add(tmp_usr)
        db.session.commit()
        flash('Create new user: %s with id: %s' % (form.name.data, tmp_usr.id))
        tagevent = get_last_tag_event()
        #flash('Add tag: %s to this user? <a herf="/crosstag/v1.0/link_user_to_last_tag/%s">YES</a>' % (tagevent.tag, tmp_usr.id))
        return render_template('new_user.html', 
            title = 'New User',
            form = form,
            message = (tmp_usr.id, tagevent.tag))
            #return redirect('/add_new_user')
    return render_template('new_user.html', 
        title = 'New User',
        form = form)

@app.route('/search_user', methods = ['GET', 'POST'])
def search_user():
    # TODO: Implement this
    form = SearchUser()
    hits = []
    if form.validate_on_submit():
        if form.id.data:
            user_id = form.id.data
            users = User.query.filter_by(id=user_id)
            hits.extend(users)
        if form.box_id.data:
            box_id = form.box_id.data
            users = User.query.filter_by(box_id=box_id)
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
            title = 'Search User',
            form = form,
            hits = ret)
    return render_template('search_user.html', 
        title = 'Search User',
        form = form)


@app.route('/all_users', methods = ['GET'])
def all_users():
    ret = []
    users = User.query.all()
    for hit in users:
        js = hit.dict()
        ret.append(js)
    return render_template('all_users.html', 
        title = 'All Users',
        hits = ret)

@app.route('/all_tagevents', methods = ['GET'])
def all_tagevents():
    ret = []
    events = Tagevent.query.all()
    for hit in events:
        js = hit.dict()
        ret.append(js)
    ret.reverse()
    return render_template('all_tagevents.html', 
        title = 'All Tagevents',
        hits = ret)

@app.route('/last_tagevents', methods = ['GET'])
def last_tagevents():
    ret = []
    events = Tagevent.query.all()[-10:]
    for hit in events:
        js = hit.dict()
        ret.append(js)
    ret.reverse()
    return render_template('all_tagevents.html', 
        title = 'Last Tagevents',
        hits = ret)

@app.route('/last_tagins', methods = ['GET'])
def last_tagins():
    ret = []
    events = Tagevent.query.all()[-10:]
    for hit in events:
        js = hit.dict()
        tag = js['tag']
        try:
            user = get_user_data_tag_dict(tag)
            js['user_id'] = user["id"]
            js['user_name'] = user['name']
        except:
            js['user_id'] = "None"
            js['user_name'] = "None"
        ret.append(js)
    ret.reverse()
    return render_template('all_tagevents.html', 
        title = 'Last Tagins',
        hits = ret)


@app.route('/edit_user/', methods = ['GET', 'POST'])
@app.route('/edit_user/<user_id>', methods = ['GET', 'POST'])
def edit_user(user_id=None):
    form = SearchUser()
    if user_id == None:
        return render_template('edit_user.html', 
            title = 'Edit User',
            form = form)
    user = User.query.filter_by(id=user_id).first()
    if form.validate_on_submit():
        user.box_id = form.box_id.data
        user.name = form.name.data
        user.email = form.email.data
        user.phone = form.phone.data
        user.tag = form.tag.data
        db.session.commit()
        flash('Updated user: %s with id: %s' % (form.name.data, user.id))
        tagevent = get_last_tag_event()
        user = User.query.filter_by(id=user_id).first()
        return render_template('edit_user.html', 
            title = 'Edit User',
            form = form,
            data = user.dict(),
            message = (user.id, tagevent.tag),
            tags = "")
    tagevents = get_tagevents_user_dict(user_id)
    return render_template('edit_user.html', 
        title = 'Edit User',
        form = form,
        data = user.dict(),
        tags = tagevents)



if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', port=80, debug = True)