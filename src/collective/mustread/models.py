# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Unicode
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class MustRead(Base):
    __tablename__ = 'mustread'

    id = Column(Integer, primary_key=True)
    userid = Column(Unicode(255), nullable=True)
    read_at = Column(DateTime, nullable=True)
    deadline = Column(DateTime, nullable=True)
    scheduled_at = Column(DateTime, nullable=True)
    scheduled_by = Column(String(255))
    status = Column(String(255), nullable=True)
    uid = Column(String(255))
    type = Column(String(255), nullable=True)
    path = Column(String(255), nullable=True)
