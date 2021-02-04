from aiogram import types, Bot

from gino import Gino
from gino.schema import GinoSchemaVisitor

from sqlalchemy.dialects.postgresql import Any
from sqlalchemy import (Column, Integer, BigInteger, String, ARRAY, ForeignKey, Date, Sequence)
from sqlalchemy.orm import relationship
from sqlalchemy import sql

from data.config import db_pass, db_user, host

db = Gino()


class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    telegram_id = Column(BigInteger)
    class_id = Column(Integer)
    name = Column(String(150))

    query: sql.Select

    def __repr__(self):
        return f"id: {self.id}, telegram: {self.telegram_id}, class: {self.class_id}"


class SchoolClass(db.Model):
    __tablename__ = 'class'

    id = Column(Integer, Sequence('class_id_seq'), primary_key=True)
    name = Column(String(50))
    telegram_chat = Column(String(50))
    members = Column(ARRAY(BigInteger))

    query: sql.Select

    def __repr__(self):
        return f"id: {self.id}, name: {self.name}"


class Notice(db.Model):
    __tablename__ = 'notice'

    id = Column(Integer, Sequence('notice_id_seq'), primary_key=True)
    class_id = Column(Integer, ForeignKey(SchoolClass.id))
    name = Column(String(250))
    body = Column(String(500))

    query: sql.Select

    school_class = relationship('SchoolClass', foreign_keys='SchoolClass.class_id')


class Events(db.Model):
    __tablename__ = 'events'

    id = Column(Integer, Sequence('event_id_seq'), primary_key=True)
    class_id = Column(Integer, ForeignKey(SchoolClass.id))
    name = Column(String(150))
    date = Column(Date())
    tasks = Column(ARRAY(String(250)))
    complete_tasks = Column(ARRAY(String(250)))

    query: sql.Select

    school_class = relationship('SchoolClass', foreign_keys='SchoolClass.class_id')


class CollectingMoney(db.Model):
    __tablename__ = 'collecting_money'

    id = Column(Integer, Sequence('money_id_seq'), primary_key=True)
    class_id = Column(Integer, ForeignKey(SchoolClass.id))
    name = Column(String(150))
    target = Column(Integer)

    query: sql.Select

    donated_money = relationship('User', backref='collecting_money', lazy='dynamic')
    school_class = relationship('SchoolClass', foreign_keys='SchoolClass.class_id')


class DBCommands:
    async def get_user(self, telegram_id):
        user = await User.query.where(User.telegram_id == telegram_id).gino.first()
        return {'user': user, 'create': False}

    async def new_user(self):
        user = types.User.get_current()

        old_user = await self.get_user(user.id)
        print(old_user)
        if old_user['user']:
            return old_user

        new_user = User()
        new_user.telegram_id = user.id
        await new_user.create()
        return {'user': new_user, 'create': True}

    async def check_in_class(self):
        user = types.User.get_current()
        user_class = await SchoolClass.query.where(Any(user.id, SchoolClass.members)).gino.all()
        return user_class

    async def get_id_class(self):
        user_class = await self.check_in_class()
        id = str(user_class[0]).split(',')[0].split(':')[1].strip()  # [id: 0, name: name]
        return id

    async def get_notice(self):
        id = await self.get_id_class()
        notices = await Notice.query.where(Notice.class_id == int(id)).gino.all()
        return notices

    async def get_notice_by_id(self, notice_id):
        notice = await Notice.query.where(Notice.id == notice_id).gino.first()
        return notice

    async def get_event(self):
        id = await self.get_id_class()
        events = await Events.query.where(Events.class_id == int(id)).gino.all()
        return events




async def create_db():
    await db.set_bind(f'postgresql://{db_user}:{db_pass}@{host}/my_class_db')

    # Create tables
    # db.gino: GinoSchemaVisitor
    # await db.gino.drop_all()
    # await db.gino.create_all()
