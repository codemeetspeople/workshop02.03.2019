"""Database models module.

The models module provides the building blocks for database metadata.

Each element within this module describes a database entity which can be
created, modified and dropped.
"""

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    inspect,
    Integer,
    ForeignKey,
    MetaData,
    Numeric,
    String,
    SmallInteger,
    TIMESTAMP,
    Text
)
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import object_session, relationship
from sqlalchemy.dialects import postgresql


__all__ = (
    'NotFoundError',
    'ModelBase',
    'Base',
)


class NotFoundError(Exception):
    """Instance not found Exception."""


class ModelBase:
    """Base Model class."""

    component = 'sdk'

    def from_dict(self, values):
        """Merge in items in the values dict into our object if it's one of our columns."""
        for c in self.__table__.columns:
            if c.name in values:
                setattr(self, c.name, values[c.name])

    @property
    def session(self):
        """Return database session."""
        return object_session(self)

    def is_relation_loaded(self, relation):
        """Check that relations was loaded."""
        return relation not in inspect(self).unloaded

    def delete(self):
        """Delete session."""
        self.session.delete(self)

    @classmethod
    def get_or_raise(cls, identity, db, exception=None, with_message=False):
        """Get object or rise 404."""
        inst = db.query(cls).get(identity)
        if inst:
            return inst
        if exception:
            raise exception()
        else:
            message = '{} #{} not found.'. format(cls.__name__, identity) if with_message else None
            raise NotFoundError(message)

    @classmethod
    def exists(cls, db, **kwargs):
        """Check if record exists in database."""
        return db.query(
            db.query(cls).filter_by(**kwargs).exists()
        ).scalar()

    @classmethod
    def truncate(cls, db):
        """Truncate faster than DELETE, because it doesn't generate scans and triggers."""
        return db.execute('TRUNCATE TABLE {}.{}'.format(cls.metadata.schema or 'public', cls.__tablename__))


metadata = MetaData()
class_registry = {}


@as_declarative(class_registry=class_registry, metadata=metadata)
class Base(ModelBase):
    """Preconfigured base class for all models."""


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    login = Column(String, nullable=False)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)

    articles = relationship("Article", back_populates="user")


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)

    articles = relationship("Article", back_populates="category")


class Article(Base):
    __tablename__ = 'article'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)

    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    category = relationship("Category", back_populates="articles")
    user = relationship("User", back_populates="articles")
