from database import Base, engine
from sqlalchemy import Column, Integer, String, TIMESTAMP, Boolean, text


def create_tables():
    Base.metadata.create_all(engine)


class PokemonData(Base):
    __tablename__ = "pokemon_data_test_3"
    # id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    id = Column(Integer, primary_key=True, server_default=text("nextval('pokemon_data_id_seq'::regclass)"), index=True)
    name = Column(String(40))
    type_1 = Column(String(40))
    type_2 = Column(String(40))
    total = Column(Integer)
    hp = Column(Integer)
    attack = Column(Integer)
    defense = Column(Integer)
    sp_atk = Column(Integer)
    sp_def = Column(Integer)
    speed = Column(Integer)
    generation = Column(Integer)
    legendary = Column(Boolean())


