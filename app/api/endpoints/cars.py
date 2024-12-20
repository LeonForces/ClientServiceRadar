from fastapi import APIRouter, Depends, Query

from fastapi_cache.decorator import cache

from typing import Annotated

from pydantic import parse_obj_as

from app.schemas.cars import SCar, SCarCreate
from app.dao.cars import CarsDAO
from app.core.exceptions import CarAlreadyExists, CarNotFound, DriverNotFound
from app.models.users import Users
from app.api.dependencies.users.dependencies import get_current_user


router = APIRouter(prefix="/cars", tags=["Cars"])


@router.post("", description="Добавление автомобиля")
async def add_car(car: SCarCreate,
                  user: Users = Depends(get_current_user)):

    return "Success"


@router.get("", description="Получение всех автомобилей")
@cache(expire=15)
async def get_cars(user: Users = Depends(get_current_user)):
    return "Success"


@router.delete("/{car_id}", description="Удаление автомобиля")
async def delete_car(car_id: int,
                     user: Users = Depends(get_current_user)):

    return "Success"


@router.put("/{car_id}", description="Изменение автомобиля")
async def update_car(car_id: int,
                     car: SCarCreate,
                     user: Users = Depends(get_current_user)):

    return "Success"
