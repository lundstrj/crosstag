# -*- coding: utf-8 -*-
from flask import Flask, jsonify, render_template, flash, redirect
import json
from generate_statistics import GenerateStats
from fortnox import Fortnox
from flask.ext.sqlalchemy import SQLAlchemy
from optparse import OptionParser
from datetime import datetime, timedelta
from forms.new_tag import NewTag
from forms.new_user import NewUser
from forms.edit_user import EditUser
from forms.search_user import SearchUser
from forms.new_debt import NewDebt
from server_helper_scripts.sync_from_fortnox import sync_from_fortnox
from server_helper_scripts.get_last_tag_event import get_last_tag_event

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
app_name = 'crosstag'


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

    def __init__(self, name, email, phone=None, address=None, address2=None, city=None, zip_code=None, tag_id=None, fortnox_id=None,
                 expiry_date=None, ssn=None, gender=None, status=None):
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

    def dict(self):
        return {'index': self.index, 'name': self.name,
                'email': self.email, 'tag_id': self.tag_id,
                'phone': self.phone, 'address': self.address,
                'address2': self.address2, 'city': self.city,
                'zip_code': self.zip_code, 'fortnox_id': self.fortnox_id,
                'expiry_date': str(self.expiry_date),
                'create_date': str(self.create_date),
                'ssn': self.ssn,
                'gender': self.gender,
                'status': self.status
                }

    def json(self):
        return jsonify(self.dict())


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


class Exercise(db.Model):
    index = db.Column(db.Integer, primary_key=True)
    exercise = db.Column(db.String(20))

    def __init__(self):
        self.exercise = None

    def dict(self):
        return {'index': self.index, 'exercise': self.exercise}

    def json(self):
        return jsonify(self.dict())


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


@app.route('/')
@app.route('/index')
@app.route('/%s' % app_name)
def index():
    return render_template('index.html')


# Renders a static page for the tagin view. Shows the person who tags in.
@app.route('/crosstag/v1.0/static_tagin_page')
def static_tagin_page():
    return render_template('static_tagin.html',
                           title='Static tagins')


# Gets all tags last month, just one event per day.
@app.route('/crosstag/v1.0/get_events_from_user_by_tag_id/<tag_id>', methods=['GET'])
def get_events_from_user_by_tag_id(tag_id):
    try:
        gs = GenerateStats()
        current_year = gs.get_current_year_string()
        counter = 0
        now = datetime.now()

        users_tagins = Tagevent.query.filter(Tagevent.tag_id.contains(tag_id)).\
            filter(Tagevent.timestamp.contains(current_year)).all()

        for tag_event in users_tagins:
            for days in range(1, 32):
                if tag_event.timestamp.month == now.month:
                    if tag_event.timestamp.day == days:
                        counter += 1
                        break

        return jsonify({"value": counter})
    except:
        return jsonify({})


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


@app.route('/all_users/<filter>', methods=['GET', 'POST'])
def all_users(filter=None):
    ret = []
    counter = 0;

    # Lists all users
    if filter == "all":
        users = User.query.order_by("expiry_date desc").all()

    # List users depending on the membership
    elif filter:
        users = User.query.filter(User.status == filter.title())

    for hit in users:

        if hit.tag_id is None or hit.tag_id == "None" or hit.tag_id == "":
            hit.tag_id = "No"
        else:
            hit.tag_id = "Yes"

        counter += 1
        js = hit.dict()
        ret.append(js)
    return render_template('all_users.html',
                           title='All Users',
                           hits=ret,
                           filter=filter,
                           count=counter)


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
        return redirect("/all_users/all")


@app.route('/add_new_user', methods=['GET', 'POST'])
def add_new_user():
    form = NewUser()
    print("errors", form.errors)
    if form.validate_on_submit():
        tmp_usr = User(form.name.data, form.email.data, form.phone.data,
                       form.address.data, form.address2.data, form.city.data,
                       form.zip_code.data, form.tag_id.data, form.fortnox_id.data,
                       form.expiry_date.data, form.birth_date.data,
                       form.gender.data)
        db.session.add(tmp_usr)
        db.session.commit()
        flash('Created new user: %s with id: %s' % (form.name.data,
                                                    tmp_usr.index))
        tagevent = get_last_tag_event()

        fortnox_data = Fortnox()
        fortnox_data.insert_customer(tmp_usr)

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


@app.route('/tagevent', methods=['GET'])
def tagevents():
        return render_template('tagevent.html',
                               title='Tagevents')


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
    return render_template('tagin_user.html', title='New tag', form=form)


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
    return redirect("/edit_user/"+str(user.index))


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


@app.route('/inactive_check', methods=['GET'])
def inactive_check():
    users = User.query.filter(User.status == "Active").all()
    arr = []
    testarr = []

    two_weeks = datetime.now() - timedelta(weeks=2)

    for user in users:

        valid_tagevent = Tagevent.query.filter(Tagevent.uid == user.index).all()[-1:]
        # valid_tagevent.reverse()
        for event in valid_tagevent:

            if event.timestamp < two_weeks:

                day_intervall = datetime.now() - event.timestamp

                temp = int(str(day_intervall)[:3])

                if temp >= 99:

                    temp = str(99) + "+"

                testarr = {'user': user, 'event': event.timestamp.strftime("%Y-%m-%d"), 'days': temp}
                arr.append(testarr)
    return render_template('inactive_check.html',
                           title='Check',
                           hits=arr)


@app.route('/debt_delete_confirm/debt_delete/<id>', methods=['POST'])
def debt_delete(id):

    debts = Debt.query.filter_by(id=id).first()
    db.session.delete(debts)
    db.session.commit()
    flash('Deleted debt: %s from member %s' % (debts.amount,
                                               debts.name))
    return redirect("/debt_check")


@app.route('/debt_delete_confirm/<id>', methods=['GET'])
def debt_delete_confirm(id):

    debts = Debt.query.filter_by(id=id).first()

    return render_template('debt_delete_confirm.html',
                           title='Delete',
                           hits=debts)


@app.route('/debt_check', methods=['GET'])
def debt_check():
    debts = Debt.query.all()

    arr = []
    testarr = []

    for hit in debts:
        testarr = {'debt': hit}
        arr.append(testarr)

    return render_template('debt_check.html',
                           title='Check',
                           hits=arr)


@app.route('/debt_create', methods=['GET', 'POST'])
def debt_create():
    form = NewDebt()
    print("errors", form.errors)
    if form.validate_on_submit():
        tmp_debt = Debt(form.amount.data, form.name.data)
        db.session.add(tmp_debt)
        db.session.commit()
        flash('Created new debt: %s for member %s' % (form.amount.data,
                                                    form.name.data))
        return redirect("/debt_check")

    return render_template('debt_create.html',
                           title='Debt Create',
                           form=form)


@app.route('/statistics', methods=['GET'])
def statistics():
    default_date = datetime.now()

    default_date_array = {'year': str(default_date.year), 'month': str(default_date.month), 'day':str(default_date.day)}

    # return default_date_array['month']
    # return default_date
    gs = GenerateStats()
    # Chosenyear, chosenmonth, chosenday

    # Fetch the data from the database.
    users = User.query.all()
    event = Tagevent

    week_day_name = default_date.strftime('%A')
    month_name = default_date.strftime('%B')
    custom_date_day = {'weekday': week_day_name + ' ' + str(default_date.day) + '/' + str(default_date.month) + '/' +
                       str(default_date.year)}

    custom_date_month = {'month': month_name + ' ' + str(default_date.year)}

    # Send the data to a method who returns an multi dimensional array with statistics.
    ret = gs.get_data(users, event, default_date_array)

    return render_template('statistics.html',
                           plot_paths='',
                           data=ret,
                           data2=custom_date_day,
                           data3=custom_date_month)


@app.route('/<_month>/<_day>/<_year>', methods=['GET'])
def statistics_by_date(_month, _day, _year):

    chosen_date_array = {'year': _year, 'month': _month, 'day': _day}

    gs = GenerateStats()
    # Chosenyear, chosenmonth, chosenday

    # Fetch the data from the database.
    users = User.query.all()
    event = Tagevent

    default_date = datetime.now()

    selected_date = default_date.replace(day=int(_day), month=int(_month), year=int(_year))

    week_day_name = selected_date.strftime('%A')
    month_name = selected_date.strftime('%B')
    custom_date_day = {'weekday': week_day_name + ' ' + str(selected_date.day) + '/' + str(selected_date.month) + '/' + str(selected_date.year)}

    custom_date_month = {'month': month_name + ' '  + str(selected_date.year)}

    # Send the data to a method who returns an multi dimensional array with statistics.
    ret = gs.get_data(users, event, chosen_date_array)

    return render_template('statistics.html',
                           plot_paths='',
                           data=ret,
                           data2=custom_date_day,
                           data3=custom_date_month)


# Syncs the local database with customers from fortnox
@app.route('/crosstag/v1.0/fortnox/', methods=['GET'])
def fortnox_users():
    sync_from_fortnox()
    flash('Local database synced with fortnox')
    return redirect("/")


# Testar fortnoxhämtning av en custom# er. 2016-02-12/ Kim, Patrik
@app.route('/fortnox/<fortnox_id>', methods=['GET'])
def fortnox_specific_user(fortnox_id):

    fortnox_data = Fortnox()

    ret = fortnox_data.get_customer_by_id(fortnox_id)

    return render_template('fortnox.html',
                           plot_paths='',
                           data=ret)


# TEST FUNKTION!!!!!
@app.route('/pb/<user_id>', methods=['GET'])
def pb(user_id):
    '''OLD SHIT, Save for future reference--------------------------------|
    tag_id = get_tag(1)
    events = Statistics.query.filter_by(tag_id=tag_id)[-20:]
    userList = users.query.join(friendships, users.id==friendships.user_id)
    .add_columns(users.userId, users.name, users.email, friends.userId, friendId)
    .filter(users.id == friendships.friend_id).filter(friendships.user_id == userID).paginate(page, 1, False)

    results = User.query.join(Statistics, User.index == Statistics.uid).add_columns(User.name, User.tag_id, Statistics.exercise, Statistics.record, Statistics.unit, Statistics.record_date, Statistics.uid).filter(User.index == user_id).filter(Statistics.uid == user_id)
    ret = []
    logging.debug("hello")
    END OF OLD SHIT----------------------------------------------------|'''

    users = User.query.filter_by(index=user_id)
    personalstats = Records.query.filter_by(uid=user_id)

    ret = []
    userret = []
    exerciseret = []

    for hit in personalstats:
        pbjs = hit.dict()
        ret.append(pbjs)

    '''exercise = Exercise.query.filter_by(index=pbjs['exercise_id'])
    exercisejs = exercise[0].dict()
    exerciseret.append(exercisejs)'''

    for hit in users:
        js = hit.dict()
        userret.append(js)

    return render_template('PB.html', plot_paths='', data=ret, users=userret, exercises=exerciseret)


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


@app.route('/user_page/<user_index>', methods=['GET', 'POST'])
def user_page(user_index=None):
    user = User.query.filter_by(index=user_index).first()

    if user is None:
        return "No user Found"

    else:

        tagevents = get_tagevents_user_dict(user_index)
        return render_template('user_page.html',
                               title='User Page',
                               data=user.dict(),
                               tags=tagevents)


@app.route('/edit_user/<user_index>', methods=['GET', 'POST'])
def edit_user(user_index=None):
    user = User.query.filter_by(index=user_index).first()
    if user is None:
        return "No user have this ID"
    form = EditUser(obj=user)
    tagevents = get_tagevents_user_dict(user_index)
    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        user.phone = form.phone.data
        user.address = form.address.data
        user.address2 = form.address2.data
        user.city = form.city.data
        user.zip_code = form.zip_code.data
        user.tag_id = form.tag_id.data
        user.gender = form.gender.data
        user.expiry_date = form.expiry_date.data
        user.status = form.status.data

        db.session.commit()
        # If we successfully edited the user, redirect back to userpage.
        fortnox_data = Fortnox()
        fortnox_data.update_customer(user)
        return redirect("/user_page/"+str(user.index))

    if user:
        return render_template('edit_user.html',
                               title='Edit User',
                               form=form,
                               data=user.dict(),
                               tags=tagevents,
                               error=form.errors)
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
    parser.add_option('--debug', dest='debug', default=False, action='store_true',
                      help="Do you want to run this thing with debug output?")
    (options, args) = parser.parse_args()
    # config['database_file'] = options.database
    # config['secret_key'] = options.secret
    db.create_all()
    # if options.debug:
    app.logger.propagate = False
    app.run(host='0.0.0.0', port=app.config["PORT"], debug=True)
