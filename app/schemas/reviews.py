from pydantic import BaseModel, field_validator
import re
from typing import Optional



class SReviewBase(BaseModel):
    id: int
    rating: int
    header: str
    description: str
    category: Optional[str] = None
    subcategory: Optional[str] = None
    reason: Optional[str] = None
    date: str



class SReviewCreate(SReviewBase):
    pass


class SReview(SReviewBase):
    pass



    class Config:
        orm_mode = True