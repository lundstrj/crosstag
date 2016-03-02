def get_last_tag_event():
    from crosstag_server import Tagevent, db

    top_index = db.session.query(db.func.max(Tagevent.index)).scalar()
    tagevent = Tagevent.query.filter_by(index=top_index).first()
    return tagevent
