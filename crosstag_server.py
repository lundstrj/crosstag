# -*- coding: utf-8 -*-
from crosstag_init import app, db, jsonify, render_template, flash, redirect, Response
import json
from generate_statistics import GenerateStats
from fortnox import Fortnox
from optparse import OptionParser
from datetime import datetime, timedelta
from forms.new_tag import NewTag
from forms.new_user import NewUser
from forms.edit_user import EditUser
from forms.search_user import SearchUser
from forms.new_debt import NewDebt
from server_helper_scripts.sync_from_fortnox import sync_from_fortnox
from server_helper_scripts.get_last_tag_event import get_last_tag_event
from server_helper_scripts.get_inactive_members import get_inactive_members
from db_models import debt
from db_models import user
from db_models import tagevent
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

User = user.User
Tagevent = tagevent.Tagevent
Debt = debt.Debt

app.config.from_pyfile('config.py')
app_name = 'crosstag'
last_tag_events = None


@app.route('/')
@app.route('/index')
@app.route('/%s' % app_name)
def index():
    return render_template('index.html')


@app.route('/stream')
def stream():
    def up_stream():
        while True:
            global last_tag_events
            tag = get_last_tag_event()
            user = None

            if last_tag_events is None or last_tag_events != tag.tag_id:
                last_tag_events = tag.tag_id

                try:
                    user = User.query.filter_by(tag_id=tag.tag_id).first().dict()
                except:
                    user = None

                if user is not None:
                    user_tagins = get_events_from_user_by_tag_id(tag.tag_id)
                    user['tagins'] = user_tagins['value']

                    return 'data: %s\n\n' % json.dumps(user)

            return 'data: %s\n\n' % user

    return Response(up_stream(), mimetype='text/event-stream')


# Renders a static page for the tagin view. Shows the person who tags in.
@app.route('/crosstag/v1.0/static_tagin_page')
def static_tagin_page():
    return render_template('static_tagin.html',
                           title='Static tagins')


@app.route('/crosstag/v1.0/static_top_five')
def static_top_five():
    try:
        users = User.query.all()
        arr = []
        one_week = datetime.now() - timedelta(weeks=1)

        if users is not None:
            for user in users:
                counter = 0
                user_tagevents = Tagevent.query.filter(Tagevent.uid == user.index).filter(Tagevent.timestamp > one_week).all()

                if user_tagevents is not None:
                    for event in user_tagevents:
                        counter += 1

                    if counter > 0:
                        person_obj = {'name': user.name, 'amount': counter}
                        arr.append(person_obj)

            new_arr = sorted(arr, key=lambda person_obj: person_obj['amount'], reverse=True)
            print(new_arr)

            return jsonify({'json_arr': [new_arr[0], new_arr[1], new_arr[2], new_arr[3], new_arr[4]]})
    except:
        return jsonify({'json_arr': None})


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

        return {"value": counter}
    except:
        return {"value": 0}


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
    counter = 0

    # Lists all users
    if filter == "all":
        users = User.query.order_by("expiry_date desc").all()
    # List users depending on the membership
    elif filter:
        users = User.query.filter(User.status == filter.title())

    for hit in users:
        counter += 1
        js = hit.dict()
        ret.append(js)
    return render_template('all_users.html',
                           title='All Users',
                           hits=ret,
                           filter=filter,
                           count=counter)


@app.route('/crosstag/v1.0/get_user_data_tag_dict/<tag_id>', methods=['GET'])
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


@app.route('/crosstag/v1.0/get_tagevents_user_dict/<user_index>', methods=['GET'])
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
    return render_template('inactive_check.html',
                           title='Check',
                           hits=get_inactive_members())


@app.route('/debt_delete_confirm/debt_delete/<id>', methods=['POST'])
def debt_delete(id):
    debts = Debt.query.filter_by(id=id).first()
    users = User.query.filter_by(index=debts.uid).first()
    db.session.delete(debts)
    db.session.commit()
    flash('Deleted debt: %s from member %s' % (debts.amount,
                                               users.name))
    return redirect("/user_page/"+str(users.index))


@app.route('/debt_delete_confirm/<id>', methods=['GET'])
def debt_delete_confirm(id):
    debts = Debt.query.filter_by(id=id).first()
    users = User.query.filter_by(index=debts.uid).first()

    return render_template('debt_delete_confirm.html',
                           title='Delete',
                           hits=debts,
                           hits2=users)


@app.route('/debt_check', methods=['GET'])
def debt_check():
    debts = Debt.query.all()
    users = User.query.all()

    debt_and_user_array = []
    multi_array = []

    for debt in debts:
        for user in users:
            if debt.uid == user.index:
                debt_and_user_array = {'debt': debt, 'user': user}
                multi_array.append(debt_and_user_array)

    return render_template('debt_check.html',
                           title='Check',
                           hits=multi_array)


@app.route('/debt_create/<id_test>', methods=['GET', 'POST'])
def debt_create(id_test):
    user = User.query.filter_by(index=id_test).first()
    form = NewDebt()

    test = datetime.now()
    print("errors", form.errors)
    if form.validate_on_submit():
        tmp_debt = Debt(form.amount.data, user.index, form.product.data, test)
        db.session.add(tmp_debt)
        db.session.commit()
        flash('Created new debt: %s for member %s' % (form.amount.data,
                                                    user.name))
        return redirect("/user_page/"+id_test)

    return render_template('debt_create.html',
                           title='Debt Create',
                           form=form,
                           error=form.errors)


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

    custom_date_month = {'month': month_name + ' ' + str(selected_date.year)}

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
    debts = Debt.query.filter_by(uid=user.index)

    if user is None:
        return "No user Found"

    else:
        tagevents = get_tagevents_user_dict(user_index)
        return render_template('user_page.html',
                               title='User Page',
                               data=user.dict(),
                               tags=tagevents,
                               debts=debts)


@app.route('/crosstag/v1.0/send_latecomers_email/', methods=['GET'])
def latecomers_mail():
    # TODO: Change the emails to correct crossfitkalmar emails
    inactive_users = get_inactive_members()
    sender = "eric.sj11@hotmail.se"
    reciver = "ej222pj@student.lnu.se"
    msg = MIMEMultipart("alternative")
    part1 = ""

    for user in inactive_users:
        temp_msg = user['user'].name + ' \r\n ' + \
                   user['user'].email + ' \r\n Telefon: ' + \
                   user['user'].phone + ' \r\n Adress: ' + \
                   user['user'].address + ' \r\n Taggade senast: ' + \
                   user['event'] + ' \r\n ' + \
                   str(user['days']) + ' dagar sedan senaste taggningen.'

        part1 = temp_msg + "\r\n\r\n" + part1

        # Converts string to UTF-8
        msg.attach(MIMEText(u'' + part1 + '', "plain", "utf-8"))

    msg.as_string().encode('ascii')

    msg['From'] = sender
    msg['To'] = reciver
    msg['Subject'] = "Medlemmar som inte har taggat på 2 veckor!"

    s = smtplib.SMTP("smtp.live.com", 587)
    # Hostname to send for this command defaults to the fully qualified domain name of the local host.
    s.ehlo()
    # Puts connection to SMTP server in TLS mode
    s.starttls()
    s.ehlo()
    s.login(sender, '')

    s.sendmail(sender, reciver, msg.as_string())

    s.quit()


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
