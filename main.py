from fastapi import FastAPI, status, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import asc, desc
from database import SessionLocal, engine
import models
import requests
from typing import Optional

app = FastAPI()
db = SessionLocal()


class Pokemon(BaseModel):
    id: int
    name: str = Field(min_length=2, max_length=30)
    type_1: str
    type_2: Optional[str] = None
    total: int
    hp: int
    attack: int
    defense: int
    sp_atk: int
    sp_def: int
    speed: int = Field(lt=200, gt=4)
    generation: int = Field(lt=7, gt=0, default=2)
    legendary: bool


@app.get("/test", status_code=200)
def getInfo():
    return {"message": "Server is running"}


@app.get('/', response_model=list[Pokemon], status_code=status.HTTP_200_OK)
def get_all_pokemon():
    getAllPokemon = db.query(models.PokemonData).all()
    # for pokemon in getAllPokemon:
    #     if pokemon.type_2 is None:
    #         pokemon.type_2 = ""
    return getAllPokemon


@app.get('/pokemon/{pokemon_id}', response_model=Pokemon, status_code=status.HTTP_200_OK)
def get_Pokemon_By_Id(pokemon_id: int):
    getSinglePokemon = db.query(models.PokemonData).filter(models.PokemonData.id == pokemon_id).first()
    if getSinglePokemon is not None:
        return getSinglePokemon
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pokemon not found..")


@app.post('/pokemon', response_model=Pokemon, status_code=status.HTTP_201_CREATED)
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
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail="Pokemon with this id is already exist..")
    else:
        db.add(newPokemon)
        db.commit()
        return newPokemon


@app.put('/pokemon/{pokemon_id}', response_model=Pokemon, status_code=status.HTTP_202_ACCEPTED)
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


@app.patch("/pokemon/{pokemon_id}", response_model=Pokemon)
def update_Pokemon_Patch(pokemon_id: str, pokemon: Pokemon):
    find_pokemon = db.query(models.PokemonData).filter(models.PokemonData.id == pokemon_id).first()
    if not find_pokemon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"pokemon with id {pokemon_id} doesn't exist...")
    for key, value in pokemon.dict(exclude_unset=True).items():
        setattr(find_pokemon, key, value)
    return find_pokemon


@app.delete('/pokemon/{pokemon_id}', response_model=Pokemon, status_code=200)
def delete_Pokemon(pokemon_id):
    find_pokemon = db.query(models.PokemonData).filter(models.PokemonData.id == pokemon_id).first()
    if find_pokemon is not None:
        db.delete(find_pokemon)
        db.commit()
        raise HTTPException(status_code=status.HTTP_200_OK, detail="Pokemon with this id is deleted successfully..")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Pokemon with this id is either alreday deleted or not found..")


@app.post("/pokemon/fetch_and_store/")
def fetch_and_store():
    response = requests.get('https://coralvanda.github.io/pokemon_data.json')
    data = response.json()
    print(f"{data}- data fetched")

    # Adjust Pokémon IDs to ensure unique
    ids = set()
    for pokemon in data:
        current_id = pokemon["#"]
        while current_id in ids:
            current_id += 1
        pokemon["#"] = current_id
        ids.add(current_id)

    # To match the database model's column names
    pokemon_data = [
        {
            "id": pokemon["#"],
            "name": pokemon["Name"],
            "type_1": pokemon["Type 1"],
            "type_2": pokemon.get("Type 2"),
            "total": pokemon["Total"],
            "hp": pokemon["HP"],
            "attack": pokemon["Attack"],
            "defense": pokemon["Defense"],
            "sp_atk": pokemon["Sp. Atk"],
            "sp_def": pokemon["Sp. Def"],
            "speed": pokemon["Speed"],
            "generation": pokemon["Generation"],
            "legendary": pokemon["Legendary"]
        }
        for pokemon in data
    ]

    try:
        # Perform bulk insert using bulk_insert_mappings
        db.bulk_insert_mappings(models.PokemonData, pokemon_data)
        db.commit()
        print("Data inserted successfully..")
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()

    return {"message": "Data successfuly stored in the database"}


@app.get("/pokemon/")
def get_pokemon(sort: str = Query("asc", description="Sort order: 'asc' or 'desc'"),
                keyword: str = Query(None, description="Search keyword"),
                col: str = Query("name", description="Column to search in, default 'name'"),
                limit: int = Query(10, description="Results per page, default 10", le=100),
                page: int = Query(1, description="Page number")):
    # Verify column exists
    if not hasattr(models.PokemonData, col):
        raise HTTPException(status_code=400, detail=f"Column '{col}' does not exist.")

    query = db.query(models.PokemonData)

    # search by keyword
    if keyword:
        query = query.filter(getattr(models.PokemonData, col).ilike(f"%{keyword}%"))

    # sorting
    if sort == "asc":
        query = query.order_by(asc(models.PokemonData.id))
    else:
        query = query.order_by(desc(models.PokemonData.id))

    # Pagination
    offset = (page - 1) * limit
    paginated_data = query.offset(offset).limit(limit).all()

    return paginated_data
