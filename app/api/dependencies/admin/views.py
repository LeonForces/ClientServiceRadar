from sqladmin import ModelView

from app.models.cars import Cars
from app.models.users import Users


class UserAdmin(ModelView, model=Users):
    column_list = [Users.id, Users.login, Users.name, Users.email, Users.telephone]
    column_details_exclude_list = [Users.hashed_password]

    can_edit = False
    can_create = True
    can_delete = True
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"


class CarAdmin(ModelView, model=Cars):
    column_list = []
    can_delete = True
    can_create = False
    can_edit = False

    name = "Car"
    name_plural = "Cars"
    icon = "fa-solid fa-car"

