from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from database import SessionLocal, engine
import models
import requests

app = FastAPI()
db = SessionLocal()


class Pokemon(BaseModel):
    id: int
    name: str
    type_1: str
    type_2: str
    total: int
    hp: int
    attack: int
    defense: int
    sp_atk: int
    sp_def: int
    speed: int
    generation: int
    legendary: bool


@app.get("/gett", status_code=200)
def getInfo():
    return {"message": "Server is running"}


@app.get('/', response_model=list[Pokemon], status_code=status.HTTP_200_OK)
def get_all_pokemon():
    getAllPokemon = db.query(models.PokemonData).all()

    for pokemon in getAllPokemon:
        if pokemon.type_2 is None:
            pokemon.type_2 = ""
    return getAllPokemon


@app.post('/addPokemon', response_model=Pokemon, status_code=status.HTTP_201_CREATED)
def add_Pokemon(pokemon: Pokemon):
    newPokemon = models.PokemonData(
        id=pokemon.id,
        name=pokemon.name,
        type_1=pokemon.type_1,
        type_2=pokemon.type_2,
        total=pokemon.total,
        hp=pokemon.hp,
        attack=pokemon.attack,
        defense=pokemon.defense,
        sp_atk=pokemon.sp_atk,
        sp_def=pokemon.sp_def,
        speed=pokemon.speed,
        generation=pokemon.generation,
        legendary=pokemon.legendary,
    )
    find_pokemon = db.query(models.PokemonData).filter(models.PokemonData.id == pokemon.id).first()
    if find_pokemon is not None:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Pokemon with this id is already exist..")
    else:
        db.add(newPokemon)
        db.commit()
        return newPokemon


@app.put('/updatePokemon/{pokemon_id}', response_model=Pokemon, status_code=status.HTTP_202_ACCEPTED)
def update_Pokemon(pokemon_id: int, pokemon: Pokemon):
    find_pokemon = db.query(models.PokemonData).filter(models.PokemonData.id == pokemon_id).first()
    if find_pokemon is not None:
        find_pokemon.id = pokemon.id
        find_pokemon.name = pokemon.name
        find_pokemon.type_1 = pokemon.type_1
        find_pokemon.type_2 = pokemon.type_2
        find_pokemon.total = pokemon.total
        find_pokemon.hp = pokemon.hp
        find_pokemon.attack = pokemon.attack
        find_pokemon.defense = pokemon.defense
        find_pokemon.sp_atk = pokemon.sp_atk
        find_pokemon.sp_def = pokemon.sp_def
        find_pokemon.speed = pokemon.speed
        find_pokemon.generation = pokemon.generation
        find_pokemon.legendary = pokemon.legendary
        db.commit()
        return find_pokemon
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pokemon with this id is not exist..")


@app.delete('/deletePokemon/{pokemon_id}', response_model=Pokemon, status_code=200)
def delete_Pokemon(pokemon_id):
    find_pokemon = db.query(models.PokemonData).filter(models.PokemonData.id == pokemon_id).first()
    if find_pokemon is not None:
        db.delete(find_pokemon)
        db.commit()
        raise HTTPException(status_code=status.HTTP_200_OK, detail="Pokemon with this id is deleted successfully..")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Pokemon with this id is either alreday deleted or not found..")


@app.get('/getById/{pokemon_id}', response_model=Pokemon, status_code=status.HTTP_200_OK)
def get_Pokemon_By_Id(pokemon_id: int):
    getSinglePokemon = db.query(models.PokemonData).filter(models.PokemonData.id == pokemon_id).first()
    if getSinglePokemon is not None:
        return getSinglePokemon
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pokemon not found..")


@app.post("/fetch-and-store/")
def fetch_and_store():
    response = requests.get('https://coralvanda.github.io/pokemon_data.json')
    data = response.json()
    print(f"{data}- data fetched")

    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            while data[i]["#"] == data[j]["#"]:
                data[j]["#"] += 1
    try:
        for pokemon in data:
            db_pokemon = models.PokemonData(
                id=pokemon['#'],
                name=pokemon['Name'],
                type_1=pokemon['Type 1'],
                type_2=pokemon.get('Type 2'),
                total=pokemon['Total'],
                hp=pokemon['HP'],
                attack=pokemon['Attack'],
                defense=pokemon['Defense'],
                sp_atk=pokemon['Sp. Atk'],
                sp_def=pokemon['Sp. Def'],
                speed=pokemon['Speed'],
                generation=pokemon['Generation'],
                legendary=pokemon['Legendary']
            )

            db.add(db_pokemon)
        db.commit()
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

    return {"message": "Data successfuly stored in the database"}

