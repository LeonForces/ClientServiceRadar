from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from app.core.db import Base


class Cars(Base):
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(primary_key=True)

    brand: Mapped[str] = mapped_column(nullable=False)
    model: Mapped[str] = mapped_column(nullable=False)
    license_plate: Mapped[str] = mapped_column(nullable=False)
    reported_issues: Mapped[int] = mapped_column(nullable=False)
    vehicle_age: Mapped[int] = mapped_column(nullable=False)
    is_working: Mapped[bool] = mapped_column(nullable=False)



    def __str__(self):

        return f"{self.bramd} | {self.model}"
