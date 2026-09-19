from datetime import datetime

from app.models import News
from app.utils import (
    generate_unique_slug,
    replace_image,
    delete_image,
)
from app.utils.constants import NEWS_FOLDER

from .base_service import BaseService


class NewsService(BaseService):

    model = News

    @classmethod
    def create_news(cls, form):

        article = News()

        form.populate_obj(article)

        article.slug = generate_unique_slug(
            News,
            article.title
        )

        article.featured_image = replace_image(
            None,
            form.featured_image.data,
            NEWS_FOLDER
        )

        if article.status == "published":
            article.published_at = datetime.utcnow()

        return cls.create(article)

    @classmethod
    def update_news(cls, article, form):

        old_status = article.status

        form.populate_obj(article)

        article.slug = generate_unique_slug(
            News,
            article.title
        )

        article.featured_image = replace_image(
            article.featured_image,
            form.featured_image.data,
            NEWS_FOLDER
        )

        if (
            old_status != "published"
            and article.status == "published"
        ):
            article.published_at = datetime.utcnow()

        cls.update()

    @classmethod
    def delete_news(cls, article):

        delete_image(
            article.featured_image,
            NEWS_FOLDER
        )

        cls.delete(article)