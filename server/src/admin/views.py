"""Model views module."""

from flask_admin.contrib.sqla import ModelView

from admin.decorators import register_view
from db import models


MODEL_VIEWS = {}


class BaseModelView(ModelView):
    """Base model view."""

    column_display_pk = True
    can_delete = False
    page_size = 100


@register_view(MODEL_VIEWS)
class UserView(BaseModelView):
    """User model view."""

    model = models.User


@register_view(MODEL_VIEWS)
class CategoryView(BaseModelView):
    """Category model view."""

    model = models.Category


@register_view(MODEL_VIEWS)
class ArticleView(BaseModelView):
    """Article model view."""

    model = models.Article
