from db_models.user import User
from db_models.tagevent import Tagevent
from datetime import datetime, timedelta

def get_inactive_members():
    users = User.query.filter(User.status == "Active").all()
    arr = []

    two_weeks = datetime.now() - timedelta(weeks=2)

    for user in users:
        valid_tagevent = Tagevent.query.filter(Tagevent.uid == user.index).all()[-1:]
        # valid_tagevent.reverse()
        for event in valid_tagevent:
            if event.timestamp < two_weeks:
                day_intervall = datetime.now() - event.timestamp

                days = int(str(day_intervall)[:3])

                if days >= 99:

                    days = str(99) + "+"

                testarr = {'user': user, 'event': event.timestamp.strftime("%Y-%m-%d"), 'days': days}
                arr.append(testarr)
    return arr