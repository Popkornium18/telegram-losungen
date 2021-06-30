from sqlalchemy import Column, Date, String, BigInteger, SmallInteger
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TagesLosung(Base):
    """Stores the Tageslosung and the corresponding Lehrtext in addition to book/verse info"""

    __tablename__ = "tageslosungen"
    date = Column(Date, primary_key=True)
    special_date = Column(String(64))
    losung = Column(String(512), nullable=False)
    losung_verse = Column(String(64), nullable=False)
    lehrtext = Column(String(512), nullable=False)
    lehrtext_verse = Column(String(64), nullable=False)

    @property
    def day_of_week(self):
        """Returns the day of the week as a number with monday being 0"""
        return self.date.weekday()

    def __repr__(self):
        return f"""TagesLosung(
  {self.date},
  {self.special_date},
  {self.day_of_week},
  {self.losung},
  {self.losung_verse},
  {self.lehrtext}
  {self.lehrtext_verse}
)"""


class JahresLosung(Base):
    """Stores the Jahreslosung as a quote and book/verse"""

    __tablename__ = "jahreslosungen"
    year = Column(SmallInteger, primary_key=True)
    losung = Column(String(512), nullable=False)
    losung_verse = Column(String(64), nullable=False)

    def __repr__(self):
        return f"""JahresLosung(
  {self.year},
  {self.losung},
  {self.losung_verse},
)"""


class Subscriber(Base):
    """Stores chat_id's of subscribed telegram users and groups"""

    __tablename__ = "subscribers"
    chat_id = Column(BigInteger, primary_key=True)

    def __repr__(self):
        return f"Subscriber({self.chat_id})"
