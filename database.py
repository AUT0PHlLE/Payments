from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    username = Column(String)
    is_premium = Column(Boolean, default=False)
    subscription_end = Column(DateTime)
    banned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    amount = Column(Float)
    payment_method = Column(String)
    transaction_id = Column(String)
    status = Column(String)  # pending, confirmed, rejected
    handle_id = Column(String)
    screenshot_file_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime)
    confirmed_by = Column(Integer)  # Admin ID who confirmed

class PaymentHandle(Base):
    __tablename__ = 'payment_handles'
    
    id = Column(Integer, primary_key=True)
    handle_id = Column(String, unique=True)
    payment_method = Column(String)
    address = Column(String)
    daily_limit = Column(Integer)
    daily_usage = Column(Integer, default=0)
    last_reset = Column(DateTime)
    is_active = Column(Boolean, default=True)

def init_db():
    Base.metadata.create_all(engine)