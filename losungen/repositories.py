"""Repository classes for all models"""
import datetime
import logging
from typing import List
from sqlalchemy import extract
from sqlalchemy.orm import Session
from losungen.models import TagesLosung, JahresLosung, Subscriber

logger = logging.getLogger(__name__)


class TagesLosungRepository:
    """Repository for TagesLosung objects"""

    def __init__(self, session: Session):
        self.session = session

    def add(self, losung: TagesLosung):
        """Persist a new TagesLosung object"""
        self.session.add(losung)
        logger.info("Added new TagesLosung for %s", losung.date)

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
        logger.info("Added new JahresLosung for %s", losung.year)

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
        logger.info("Added new subscriber %i", subscriber.chat_id)

    def delete(self, subscriber: Subscriber):
        """Delete an existing Subscriber object from the database"""
        self.session.delete(subscriber)
        logger.info("Deleted subscriber %i", subscriber.chat_id)

    def get_by_id(self, chat_id: int) -> Subscriber:
        """Get the Subscriber with a specific ID"""
        return self.session.query(Subscriber).filter_by(chat_id=chat_id).first()

    def list(self) -> List[Subscriber]:
        """Get all Subscriber objects"""
        return self.session.query(Subscriber).all()
