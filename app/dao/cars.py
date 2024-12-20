from sqlalchemy import select

from app.dao.base import BaseDAO
from app.models.cars import Cars
from app.core.db import async_session_maker


class CarsDAO(BaseDAO):

    model = Cars

    @classmethod
    async def find_by_number(cls, license_plate: str):

        async with async_session_maker() as session:

            query = select(Cars).filter_by(license_plate=license_plate)
            result = await session.execute(query)
            return result.one_or_none()
