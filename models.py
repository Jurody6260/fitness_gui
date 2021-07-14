from sqlalchemy import func, and_, delete, create_engine, text, MetaData, Integer, String, Column, ForeignKey, Date, Time, DateTime, Boolean, extract
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, subqueryload, joinedload, relationship
from datetime import date, time, datetime
import serial
import os
import threading
import pandas as pd
from openpyxl import Workbook
from json import loads, dumps, load, dump
# us = User(name="Azamat", RFID="12345678", tel="123123", schedule_id=""
from time import sleep
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy').setLevel(logging.ERROR)

meta = MetaData()
Base = declarative_base()
engine = create_engine("sqlite:///fitness.db")


Session = sessionmaker(bind=engine)
session = Session()


def reboot():
    os.system("sudo reboot")


def delete_coach(coach):
    session.query(Coach).filter_by(id=coach).delete()
    session.commit()


def delete_sch(sch):
    if session.query(User).filter_by(schedule_id=sch).first():
        for i in session.query(User).filter_by(schedule_id=sch).all():
            i.schedule_id = session.query(
                Schedule).order_by(Schedule.id).first().id
    session.query(Schedule).filter_by(id=sch).delete()
    session.commit()


def delete_user(usr):
    session.query(User).filter_by(id=usr).delete()
    session.commit()


def search_coach():
    return session.query(Coach).all()


def search_schedule():
    return session.query(Schedule).all()


def search_payments():
    if len(str(datetime.now().month)) == 1:
        month = str(datetime.now().month)
        month = '0' + month
    return session.query(Payment).filter(extract('month', Payment.action_time) >= datetime.today().month, extract('year', Payment.action_time) >= datetime.today().year, extract('day', Payment.action_time) >= datetime.today().day).all()


def search_actions(session):
    return session.query(Action).order_by(Action.id.desc()).limit(20).all()


def add_RFID(id, RFID):
    usr = session.query(User).filter_by(id=id).first()
    usr.RFID = RFID
    session.add(usr)
    session.commit()


def create_schedule(name, start_time, end_time, train_amount):
    if name != '' and len(start_time.split(":")) == 2 and len(end_time.split(":")) == 2 and train_amount != '':
        sch = Schedule(name=name, start_time=start_time,
                       end_time=end_time, train_amount=train_amount)
        session.add(sch)
        session.commit()


def create_payment(user_id, money, coach_id):
    if user_id != '' and money != '' and coach_id != '' and len(session.query(User).filter_by(id=user_id).all()) != 0 and len(session.query(Coach).filter_by(id=coach_id).all()) != 0:
        pay = Payment(user_id=user_id, money=money,
                      coach_id=coach_id, action_time=datetime.now())
        session.add(pay)
        session.commit()


def create_coach(name):
    if name != '':
        coa = Coach(name=name)
        session.add(coa)
        session.commit()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    RFID = Column(String(8), unique=True)
    name = Column(String, nullable=False)
    tel = Column(String, nullable=False)
    schedule_id = Column(Integer, ForeignKey("schedule.id"), nullable=False)
    start_date = Column(String)  # default=date.today()
    end_date = Column(String)
    train_amount = Column(Integer, default=10, nullable=False)
    registered_on = Column(Date, nullable=False)
    user_level = Column(Integer, default=0)
    schedule = relationship("Schedule", back_populates="user")
    action = relationship("Action", back_populates="user")
    payment = relationship("Payment", back_populates="user")

    def format(self):
        return {
            "id": self.id,
            "RFID": self.RFID,
            "name": self.name,
            "tel": self.tel,
            "schedule_id": self.schedule_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "train_amount": self.train_amount,
            "registered_on": self.registered_on,
            "user_level": self.user_level
        }


class Schedule(Base):
    __tablename__ = 'schedule'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    start_time = Column(String, nullable=False)  # default=time.now()
    end_time = Column(String, nullable=False)
    train_amount = Column(Integer, nullable=False)
    user = relationship("User", back_populates="schedule")

    def format(self):
        return {
            "id": self.id,
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "train_amount": self.train_amount
        }


class Action(Base):
    __tablename__ = "action"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    action_time = Column(DateTime, default=datetime.now())
    is_entry = Column(Boolean, nullable=False)
    allowed = Column(Boolean, nullable=False)
    user = relationship("User", back_populates="action")

    def format(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action_time": self.action_time,
            "is_entry": self.is_entry,
        }


class Payment(Base):
    __tablename__ = "payment"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    action_time = Column(DateTime, default=datetime.now())
    money = Column(Integer, nullable=False)
    coach_id = Column(Integer, ForeignKey("coach.id"), nullable=False)
    user = relationship("User", back_populates="payment")
    coach = relationship("Coach", back_populates="payment")

    def format(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action_time": self.action_time,
            "money": self.money,
            "coach_id": self.coach_id,
        }


class Coach(Base):
    __tablename__ = "coach"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    payment = relationship("Payment", back_populates="coach")

    def format(self):
        return {
            "id": self.id,
            "name": self.name
        }


# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
session.close()

# 8765AB12 1234AB12
