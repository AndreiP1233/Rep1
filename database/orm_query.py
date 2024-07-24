from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import People, Jobs

async def add_person(session:AsyncSession, data, user_id):
    obj = People(
        name=data['name'],
        year=data['year'],
        date=data['date'],
        user_id=user_id,
    )
    session.add(obj)
    await session.commit()

async def get_people_info(session:AsyncSession, user_id):
    query = select(People).where(People.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()

async def get_person_data(session:AsyncSession, person_id):
    query = select(People).where(People.id == person_id)
    result = await session.execute(query)
    return result.scalar()

async def delete_person(session:AsyncSession, person_id):
    query = delete(People).where(People.id == person_id)
    await session.execute(query)
    await session.commit()

async def add_job(session:AsyncSession, job_id, person_id):
    obj = Jobs(
        job_id=job_id,
        person_id=person_id,
    )
    session.add(obj)
    await session.commit()

async def get_person_jobs(session:AsyncSession, person_id):
    query = select(Jobs).where(Jobs.person_id == person_id)
    result = await session.execute(query)
    return result.scalars().all()

async def delete_job(session:AsyncSession, person_id):
    query = delete(Jobs).where(Jobs.person_id == person_id)
    await session.execute(query)
    await session.commit()

async def update_person(session:AsyncSession, person_id, data):
    query = update(People).where(People.id == person_id).values(
        name=data['name'],
        year=data['year'],
        date=data['date'],
    )
    await session.execute(query)
    await session.commit()
