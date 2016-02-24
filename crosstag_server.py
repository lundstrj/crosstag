# -*- coding: utf-8 -*-
from flask import Flask, jsonify, render_template, flash, redirect
import json
from io import StringIO
from generate_statistics import GenerateStats
#ta bort fortnox här sen
from fortnox import Fortnox
from flask.ext.sqlalchemy import SQLAlchemy
from optparse import OptionParser
from datetime import datetime, timedelta
from forms.new_tag import NewTag
from forms.new_user import NewUser
from forms.edit_user import EditUser
from forms.search_user import SearchUser

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
app_name = 'crosstag'


#Implementerade status i user, skriver bara ut siffra atm. // Rydberg 2016-02-10.
class Member_status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(12))

    def __init__(self, id, status):
        self.id = id
        self.status = status

    def dict(self):
        return {'id': self.id, 'status': self.status}

    def json(self):
        return jsonify(self.dict())


class User(db.Model):
    index = db.Column(db.Integer, primary_key=True)
    fortnox_id = db.Column(db.Integer)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120))
    phone = db.Column(db.Integer)
    address = db.Column(db.String(50))
    address2 = db.Column(db.String(50))
    city = db.Column(db.String(120))
    zip_code = db.Column(db.Integer)
    tag_id = db.Column(db.String(12))
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

        if js != None:#Vi får ut tag id så att man enklare kan lägga till det på en ny medlem!
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
        return {'id': self.id, 'exercise_id': self.exercise_id, 'record': self.record, 'unit': self.unit, 'record_date': self.record_date, 'uid':self.uid}

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



def get_last_tag_event():
    top_index = db.session.query(db.func.max(Tagevent.index)).scalar()
    tagevent = Tagevent.query.filter_by(index=top_index).first()
    return tagevent


# Syncs the fortnox database with the local DB
def sync_from_fortnox():
    fortnox_data = Fortnox()

    customers = fortnox_data.get_all_customers()
    ret = []

    for customer in customers:
        cust = {'FortnoxID': customer["CustomerNumber"],
                'OrganisationNumber': customer['OrganisationNumber'],
                'Name': customer["Name"],
                'Email': customer['Email'],
                'Phone': customer['Phone'],
                'Address1': customer['Address1'],
                'Address2': customer['Address2'],
                'City': customer['City'],
                'Zipcode': customer['ZipCode']}

        ret.append(cust)

    for customer in ret:
        if User.query.filter_by(fortnox_id=customer['FortnoxID']).first() is not None:
            update_user_in_local_db_from_fortnox(customer)
        else:
            add_user_to_local_db_from_fortnox(customer)


# Updating an existing user in local DB from fortnox.
def update_user_in_local_db_from_fortnox(customer):
    user = User.query.filter_by(fortnox_id=customer['FortnoxID']).first()
    if user is None:
        return "she wrote upon it; no such number, no such zone"
    else:
        user.name = customer['Name']
        user.email = customer['Email']
        user.phone = customer['Phone']
        user.address = customer['Address1']
        user.address2 = customer['Address2']
        user.city = customer['City']
        user.zip_code = customer['Zipcode']
        user.gender = user.gender
        user.ssn = customer['OrganisationNumber']
        user.expiry_date = user.expiry_date
        user.create_date = user.create_date

        db.session.commit()


# Adding a fortnox user to the local DB
def add_user_to_local_db_from_fortnox(customer):
    tmp_usr = User(customer['Name'], customer['Email'], customer['Phone'],
                       customer['Address1'], customer['Address2'], customer['City'],
                       customer['Zipcode'], None, customer['FortnoxID'],
                        None, customer['OrganisationNumber'],
                       None, None)
    db.session.add(tmp_usr)
    db.session.commit()


@app.route('/')
@app.route('/index')
@app.route('/%s' % app_name)
def index():
    return render_template('index.html')


@app.route('/crosstag/v1.0/static_tagin_page')
def static_tagin_page():
    return  render_template('static_tagin.html',
                            title='Static tagins')


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
                       form.address.data, form.address2.data, form.city.data,
                       form.zip_code.data, form.tag_id.data, form.fortnox_id.data,
                       form.expiry_date.data, form.birth_date.data,
                       form.gender.data)
        db.session.add(tmp_usr)
        db.session.commit()
        flash('Created new user: %s with id: %s' % (form.name.data,
                                                    tmp_usr.index))
        tagevent = get_last_tag_event()

        fortnoxData = Fortnox()
        fortnoxData.insert_customer(tmp_usr)

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
                               title='Tagevents',
                                )



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


@app.route('/inactive_check', methods=['GET'])
def inactive_check():

    users = User.query.all()
    arr = []
    testarr = []

    two_weeks = datetime.now() - timedelta(weeks=2)

    for user in users:

        valid_tagevent = Tagevent.query.filter(Tagevent.uid == user.index).all()
        valid_tagevent.reverse()
        for event in valid_tagevent:

            if event.timestamp < two_weeks:

                day_intervall = datetime.now() - event.timestamp

                temp = int(str(day_intervall)[:3])

                if temp >= 99:

                    temp = str(99) + "+"


                testarr = {'user': user, 'event': event.timestamp.strftime("%Y-%m-%d"), 'days': temp}
                arr.append(testarr)

                break


    return render_template('inactive_check.html',
                           title='Check',
                           hits=arr)



@app.route('/statistics', methods=['GET'])
def statistics():

    default_date = datetime.now()

    defaultDateArray = {'year': str(default_date.year), 'month': str(default_date.month), 'day':str(default_date.day)}

    #return defaultDateArray['month']
    #return default_date
    gs = GenerateStats()
    #Chosenyear, chosenmonth, chosenday

    # Fetch the data from the database.
    users = User.query.all()
    event = Tagevent

    weekDayName = default_date.strftime('%A')
    monthName = default_date.strftime('%B')
    customDateDay = {'weekday': weekDayName + ' '     + str(default_date.day) + '/' + str(default_date.month) + '/' + str(default_date.year)}

    customDateMonth = {'month': monthName + ' '  + str(default_date.year)}

    # Send the data to a method who returns an multi dimensional array with statistics.
    ret = gs.get_data(users, event, defaultDateArray)

    return render_template('statistics.html',
                           plot_paths='',
                           data=ret,
                           data2=customDateDay,
                           data3=customDateMonth)


@app.route('/<_month>/<_day>/<_year>', methods=['GET'])
def statistics_by_date(_month, _day, _year):

    chosenDateArray = {'year': _year, 'month': _month, 'day': _day}



    gs = GenerateStats()
    #Chosenyear, chosenmonth, chosenday

    # Fetch the data from the database.
    users = User.query.all()
    event = Tagevent

    default_date = datetime.now()

    selected_date = default_date.replace(day=int(_day), month=int(_month), year=int(_year))

    weekDayName = selected_date.strftime('%A')
    monthName = selected_date.strftime('%B')
    customDateDay = {'weekday': weekDayName + ' ' + str(selected_date.day) + '/' + str(selected_date.month) + '/' + str(selected_date.year)}

    customDateMonth = {'month': monthName + ' '  + str(selected_date.year)}

    # Send the data to a method who returns an multi dimensional array with statistics.
    ret = gs.get_data(users, event, chosenDateArray)

    return render_template('statistics.html',
                           plot_paths='',
                           data=ret,
                           data2=customDateDay,
                           data3=customDateMonth)


# Syncs the local database with customers from fortnox
@app.route('/crosstag/v1.0/fortnox/', methods=['GET'])
def fortnox_users():
    sync_from_fortnox()
    flash('Local database synced with fortnox')
    return redirect("/")


# Testar fortnoxhämtning av en custom# er. 2016-02-12/ Kim, Patrik
@app.route('/fortnox/<fortnox_id>', methods=['GET'])
def fortnox_specific_user(fortnox_id):

    fortnoxData = Fortnox()

    ret = fortnoxData.get_customer_by_id(fortnox_id)

    return render_template('fortnox.html',
                           plot_paths='',
                           data=ret)

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
        return "she wrote upon it; no such number, no such zone"
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
        ##If we successfully edited the user, redirect back to userpage.
        fortnoxData = Fortnox()
        fortnoxData.update_customer(user)
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
    parser.add_option('--debug', dest='debug', default=False, action='store_true', help="Do you want to run this thing with debug output?")
    (options, args) = parser.parse_args()
    #config['database_file'] = options.database
    #config['secret_key'] = options.secret
    db.create_all()
    #if options.debug:
    app.logger.propagate = False
    app.run(host='0.0.0.0', port=app.config["PORT"], debug=True)


