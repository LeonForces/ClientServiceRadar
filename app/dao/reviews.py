from sqlalchemy import select

from app.dao.base import BaseDAO
from app.models.reviews import Reviews
from app.core.db import async_session_maker


class ReviewsDAO(BaseDAO):

    model = Reviews

    @classmethod
    async def find_by_header(cls, header: str):

        async with async_session_maker() as session:

            query = select(Reviews).filter_by(header=header)
            result = await session.execute(query)
            return result.one_or_none()
