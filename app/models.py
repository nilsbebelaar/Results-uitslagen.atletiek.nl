from app import db
import json
from sqlalchemy import asc, desc


class Competitions(db.Model):
    __tablename__ = 'Competitions'
    id = db.Column(db.Integer, primary_key=True)

    athletes = db.Column(db.String())
    resultlists = db.Column(db.String())
    number_of_lists = db.Column(db.Integer())

    begindate = db.Column(db.String(10))
    enddate = db.Column(db.String(10))
    date_print = db.Column(db.String(20))
    days = db.Column(db.Integer())

    source = db.Column(db.String(100))
    domain = db.Column(db.String(100))
    location = db.Column(db.String(100))
    country = db.Column(db.String(5))
    name = db.Column(db.String(200))

    status = db.Column(db.String(20))

    url = db.Column(db.String(100))

    def __repr__(self):
        return '<Wedstrijd: {}>'.format(self.name)

    @staticmethod
    def load_dict(id):
        comp = Competitions.query.get(id)
        if comp:
            comp = comp.__dict__
        else:
            return None
        comp['athletes'] = json.loads(comp['athletes'])
        comp['resultlists'] = json.loads(comp['resultlists'])
        return comp

    @staticmethod
    def save_dict(comp_in):
        new = False
        comp = Competitions.query.get(comp_in['id'])
        if not comp:
            new = True
            comp = Competitions()

        keys = [k for k in comp_in.keys() if k not in ['athletes', 'resultlists', '_sa_instance_state']]
        for key in keys:
            setattr(comp, key, comp_in[key])
        comp.number_of_lists = len(comp_in['resultlists'] if 'resultlists' in comp_in else [])
        comp.athletes = json.dumps(comp_in['athletes'] if 'athletes' in comp_in else [])
        comp.resultlists = json.dumps(comp_in['resultlists'] if 'resultlists' in comp_in else [])

        if new:
            db.session.add(comp)
        db.session.commit()

    @staticmethod
    def list():
        return Competitions.query.order_by(desc(Competitions.begindate)).all()
