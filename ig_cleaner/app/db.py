from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime

from .config import DB_URL

Base = declarative_base()

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    profile_id = Column(String)  # MoreLogin profile ID
    proxy = Column(String)
    status = Column(String, default='active')  # active/quarantine/manual
    last_successful_login = Column(DateTime)
    last_run = Column(DateTime)
    enabled = Column(Boolean, default=True)
    two_fa = Column(Boolean, default=False)
    password_encrypted = Column(String)

    deletions = relationship("Deletion", back_populates="account")

class Deletion(Base):
    __tablename__ = 'deletions'
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    media_id = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String)  # success/failed
    note = Column(String)

    account = relationship("Account", back_populates="deletions")

class Schedule(Base):
    __tablename__ = 'schedules'
    id = Column(Integer, primary_key=True)
    cron_expr = Column(String)
    target_account_ids = Column(String)  # Can be a comma-separated list of IDs or 'all'
    enabled = Column(Boolean, default=True)

engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    init_db()
    print("Database initialized.")
