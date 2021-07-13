from datetime import date as dt
from sqlalchemy import extract
from losungen.models import TagesLosung, JahresLosung, Subscriber

class TagesLosungRepository():
    def __init__(self, session):
        self.session = session

    def add(self, losung):
        self.session.add(losung)

    def get_by_date(self, date=None):
        date = dt.today() if date is None else date
        return self.session.query(TagesLosung).filter_by(date=date).first()

    def get_by_year(self, year=None):
        year = dt.today().year if year is None else year
        return self.session.query(TagesLosung).filter(extract('year', TagesLosung.date) == year).all()

    def list(self):
        return self.session.query(TagesLosung).all()


class JahresLosungRepository():
    def __init__(self, session):
        self.session = session

    def add(self, losung):
        self.session.add(losung)

    def get_by_year(self, year=None):
        year = dt.today().year if year is None else year
        return self.session.query(JahresLosung).filter_by(date=year).all()

    def list(self):
        return self.session.query(JahresLosung).all()


class SubscriberRepository():
    def __init__(self, session):
        self.session = session

    def add(self, subscriber):
        self.session.add(subscriber)

    def delete(self, subscriber):
        self.session.delete(subscriber)

    def get_by_id(self, chat_id):
        return self.session.query(Subscriber).filter_by(chat_id=chat_id).first()

    def list(self):
        return self.session.query(Subscriber).all()
