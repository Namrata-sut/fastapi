from faker import Faker
from app.models.models import PokemonData

fake = Faker()


class PokemonFactory:
    sqlalchemy_session = None

    @classmethod
    def set_session(cls, session):
        """Sets the SQLAlchemy session for the factory."""
        cls.sqlalchemy_session = session

    @classmethod
    def create_pokemon(cls, session=None, **kwargs):
        """Creates a new Pokemon object, persists it to the database, and returns it."""
        session = session or cls.sqlalchemy_session

        if session is None:
            raise ValueError("A valid SQLAlchemy session is required to create Pokemon.")

        pokemon_data = {
            "name": kwargs.get("name", fake.first_name()),
            "type_1": kwargs.get("type_1", "Normal"),
            "type_2": kwargs.get("type_2", None),
            "total": kwargs.get("total", 300),
            "hp": kwargs.get("hp", 50),
            "attack": kwargs.get("attack", 50),
            "defense": kwargs.get("defense", 50),
            "sp_atk": kwargs.get("sp_atk", 50),
            "sp_def": kwargs.get("sp_def", 50),
            "speed": kwargs.get("speed", 50),
            "generation": kwargs.get("generation", 1),
            "legendary": kwargs.get("legendary", False)
        }

        pokemon = PokemonData(**pokemon_data)

        session.add(pokemon)
        session.commit()
        session.refresh(pokemon)

        return pokemon
