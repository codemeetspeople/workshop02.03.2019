from factory.alchemy import SQLAlchemyModelFactory

from db.manager import db_factory
from db.models import (
    User, Category, Article
)

test_session = db_factory(master=True, autocommit=True, autoflush=True)


class SessionProxy(object):
    DEFAULT_FACTORY_SESSION = test_session
    session = DEFAULT_FACTORY_SESSION

    def add(self, item):
        self.session.add(item)

    def commit(self):
        if not self.session.autocommit:
            self.session.commit()
        else:
            self.session.flush()

    def query(self, *args, **kwargs):
        return self.session.query(*args, **kwargs)


class ModelFactory(SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = SessionProxy()

    @classmethod
    def create(cls, **kwargs):
        ret = super(SQLAlchemyModelFactory, cls).create(**kwargs)
        cls._meta.sqlalchemy_session.commit()
        return ret

    @classmethod
    def create_batch(cls, size, **kwargs):
        ret = [super(SQLAlchemyModelFactory, cls).create(**kwargs) for _ in range(size)]
        cls._meta.sqlalchemy_session.commit()
        return ret

    @classmethod
    def cleanup(cls):
        affected_models = getattr(cls, '_affected_models', [])
        cls._meta.sqlalchemy_session.query(cls._meta.model).delete()
        for model in affected_models:
            cls._meta.sqlalchemy_session.query(model).delete()


class UserFactory(ModelFactory):
    class Meta:
        model = User


class CategoryFactory(ModelFactory):
    class Meta:
        model = Category


class ArticleFactory(ModelFactory):
    class Meta:
        model = Article


factories_list = (
    UserFactory,
    CategoryFactory,
    ArticleFactory
)
