from sqladmin import ModelView

from app.models.reviews import Reviews
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


class ReviewAdmin(ModelView, model=Reviews):
    column_list = []
    can_delete = True
    can_create = False
    can_edit = False

    name = "Review"
    name_plural = "Reviews"
    icon = "fa-solid fa-review"

