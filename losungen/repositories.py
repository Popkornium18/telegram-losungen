"""Repository classes for all models"""
import datetime
from typing import List
from sqlalchemy import extract
from sqlalchemy.orm import Session
from losungen.models import TagesLosung, JahresLosung, Subscriber


class TagesLosungRepository:
    """Repository for TagesLosung objects"""

    def __init__(self, session: Session):
        self.session = session

    def add(self, losung):
        """Persist a new TagesLosung object"""
        self.session.add(losung)

    def get_by_date(self, date: datetime.date = None) -> TagesLosung:
        """Get the TagesLosung for a given date.
        The date parameter defaults to today"""
        date = datetime.date.today() if date is None else date
        return self.session.query(TagesLosung).filter_by(date=date).first()

    def get_by_year(self, year: int = None) -> List[TagesLosung]:
        """Get all TagesLosung objects for a given year.
        The year parameter defaults to the current year."""
        year = datetime.date.today().year if year is None else year
        return (
            self.session.query(TagesLosung)
            .filter(extract("year", TagesLosung.date) == year)
            .all()
        )

    def list(self) -> List[TagesLosung]:
        """Get all TagesLosung objects"""
        return self.session.query(TagesLosung).all()


class JahresLosungRepository:
    """Repository for JahresLosung objects"""

    def __init__(self, session: Session):
        self.session = session

    def add(self, losung: JahresLosung):
        """Persist a new JahresLosung object"""
        self.session.add(losung)

    def get_by_year(self, year: int = None) -> JahresLosung:
        """Get the JahresLosung for a given year.
        The year parameter defaults to the current year"""
        year = datetime.date.today().year if year is None else year
        return self.session.query(JahresLosung).filter_by(date=year).first()

    def list(self) -> List[JahresLosung]:
        """Get all JahresLosung objects"""
        return self.session.query(JahresLosung).all()


class SubscriberRepository:
    """Repository for Subscriber objects"""

    def __init__(self, session: Session):
        self.session = session

    def add(self, subscriber: Subscriber):
        """Persist a new Subscriber object"""
        self.session.add(subscriber)

    def delete(self, subscriber: Subscriber):
        """Delete an existing Subscriber object from the database"""
        self.session.delete(subscriber)

    def get_by_id(self, chat_id: int) -> Subscriber:
        """Get the Subscriber with a specific ID"""
        return self.session.query(Subscriber).filter_by(chat_id=chat_id).first()

    def list(self) -> List[Subscriber]:
        """Get all Subscriber objects"""
        return self.session.query(Subscriber).all()
