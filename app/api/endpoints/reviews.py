from fastapi import APIRouter, Depends, Query

from fastapi_cache.decorator import cache

from typing import Annotated

from pydantic import parse_obj_as

from app.schemas.reviews import SReview
from app.dao.reviews import ReviewsDAO
from app.models.users import Users
from app.api.dependencies.users.dependencies import get_current_user
from datetime import date


router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("", description="Добавление отзыва")
async def add_review(header: Annotated[str, Query(description="Заголовок")],
                     description: Annotated[str, Query(description="Описание")],
                     rating: Annotated[str, Query(description="Оценка")],
                     user: Users = Depends(get_current_user)):
    await ReviewsDAO.add(header=header, description=description, rating=rating, date=date.today().strftime("%Y-%m-%d"))
    return "Success"


@router.get("", description="Получение отзывов")
@cache(expire=15)
async def get_reviews(user: Users = Depends(get_current_user)):
    reviews = await ReviewsDAO.find_last_some()
    reviews_json = parse_obj_as(list[SReview], reviews)
    return reviews_json


# @router.delete("/{id}", description="Удаление")
# async def delete(id: int, user: Users = Depends(get_current_user)):
#
#     return "Success"
#
#
# @router.put("/{id}", description="Изменение автомобиля")
# async def update(id: int, user: Users = Depends(get_current_user)):
#
#     return "Success"
