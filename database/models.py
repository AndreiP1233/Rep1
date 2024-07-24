from sqlalchemy import DateTime, Float, String, Text, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, declarative_base

class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class People(Base):
    __tablename__ = 'people'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    year: Mapped[int] = mapped_column(String(4))
    date: Mapped[str] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(String(150))

    jobs = relationship('Jobs', back_populates='person')


class Jobs(Base):
    __tablename__ = 'job_people'

    job_id: Mapped[int] = mapped_column(String(190), primary_key=True)
    person_id: Mapped[int] = mapped_column(ForeignKey('people.id',ondelete='CASCADE'), primary_key=True)

    person = relationship('People', back_populates='jobs')
