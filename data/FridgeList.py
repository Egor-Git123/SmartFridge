import datetime
import sqlalchemy
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class FridgeList(SqlAlchemyBase):
    __tablename__ = 'product'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id =  sqlalchemy.Column(sqlalchemy.Integer, autoincrement=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    type = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    f_date = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    l_date = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    weight = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    calories = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    total = sqlalchemy.Column(sqlalchemy.String, nullable=False)
