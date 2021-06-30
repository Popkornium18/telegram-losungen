from losungen.models import Base
from config import cfg
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(cfg["DB"], future=True)
Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)
