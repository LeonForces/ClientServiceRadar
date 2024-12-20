from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Review(BaseModel):
    id: int
    rate: float
    header: str
    description: str

# Фиктивные данные для примера
reviews = [
    Review(id=1, rate=4.0, header="Отличный сервис!", description="Быстрое обслуживание и вежливый персонал."),
    Review(id=2, rate=3.5, header="Хороший опыт", description="Цены немного завышены, но качество товаров радует."),
    Review(id=3, rate=2.0, header="Не оправдал ожиданий", description="Товар пришел поврежденным, пришлось возвращать.")
]

@app.get("/reviews/", response_model=List[Review])
async def get_reviews():
    return reviews