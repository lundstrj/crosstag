from db_models.user import User
from db_models.tagevent import Tagevent
from datetime import datetime, timedelta


def get_inactive_members():
    users = User.query.filter(User.status == "Active").filter(User.last_tag_timestamp is not None).filter(User.last_tag_timestamp != '').all()
    arr = []

    two_weeks = datetime.now() - timedelta(weeks=2)

    for user in users:
        if user.last_tag_timestamp < two_weeks:
            day_intervall = datetime.now() - user.last_tag_timestamp

            days = int(str(day_intervall)[:3])

            if days >= 99:

                days = str(99) + "+"

            testarr = {'user': user, 'event': user.last_tag_timestamp.strftime("%Y-%m-%d"), 'days': days}
            arr.append(testarr)
    return arr
