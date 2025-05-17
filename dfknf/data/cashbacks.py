import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Cashback(SqlAlchemyBase):
    __tablename__ = 'cashbacks'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    category = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    amount_spent = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    cashback_expected = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship("User")