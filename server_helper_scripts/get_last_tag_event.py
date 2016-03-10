from crosstag_init import db
from db_models.tagevent import Tagevent


def get_last_tag_event():
    #top_index = db.session.query(db.func.max(Tagevent.index)).scalar()
    #tagevent = Tagevent.query.filter_by(index=top_index).first()
    tagevent = Tagevent.query.first()
    if tagevent == None:
        return None
    else:
        return tagevent
