import enum
from sqlalchemy import Column, Integer, String, Boolean, Enum
from src.app.database.database import Base, engine


def create_tables():
    Base.metadata.create_all(engine)


class PokemonData(Base):
    __tablename__ = "pokemon_data"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True, index=True, extend_existing=True)
    # id = Column(
    #     Integer,
    #     primary_key=True,
    #     server_default=text("nextval('pokemon_data_id_seq'::regclass)"),
    #     index=True,
    # )
    name = Column(String(40), nullable=False)
    type_1 = Column(String(40), nullable=False)
    type_2 = Column(String(40), nullable=True)
    total = Column(Integer, nullable=False)
    hp = Column(Integer, nullable=False)
    attack = Column(Integer, nullable=False)
    defense = Column(Integer, nullable=False)
    sp_atk = Column(Integer, nullable=False)
    sp_def = Column(Integer, nullable=False)
    speed = Column(Integer, nullable=False)
    generation = Column(Integer, nullable=False)
    legendary = Column(Boolean(), nullable=False)


class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"
    moderator = "moderator"


class Users(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, extend_existing=True)
    username = Column(String(40), nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)