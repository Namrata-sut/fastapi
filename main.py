from typing import Optional

from fastapi import FastAPI, status, HTTPException, Query
from pydantic import BaseModel, Field
import requests
from sqlalchemy import asc, desc, func, inspect, Integer, Boolean, String
from sqlalchemy.orm import mapper

from database import SessionLocal, engine
import models

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


@app.get('/pokemon/{pokemon_id}', response_model=Pokemon, status_code=status.HTTP_200_OK)
def get_Pokemon_By_Id(pokemon_id: int):
    getSinglePokemon = db.query(models.PokemonData).filter(models.PokemonData.id == pokemon_id).first()
    if getSinglePokemon is not None:
        return getSinglePokemon
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pokemon not found..")


@app.post('/pokemon', response_model=Pokemon, status_code=status.HTTP_201_CREATED)
def add_Pokemon(pokemon: Pokemon):
    # max_id = db.query(func.max(models.PokemonData.id)).scalar()
    # new_id = (max_id or 0) + 1
    newPokemon = models.PokemonData(
        # id=new_id,
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
    # find_pokemon = db.query(models.PokemonData).filter(models.PokemonData.id == pokemon.id).first()
    # if find_pokemon is not None:
    #     raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
    #                         detail="Pokemon with this id is already exist..")
    # else:
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
    # print(f"{data}- data fetched")

    # Adjust Pokémon IDs to ensure unique
    # ids = set()
    # for pokemon in data:
    #     if pokemon["#"] in ids:
    #         pokemon["#"] = max(ids) + 1
    #         ids.add(pokemon["#"])

    # To match the database model's column names
    pokemon_data = [
        {
            # "id": pokemon["#"],
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
                keyword: Optional[str] = Query(None, description="Search keyword"),
                col: str = Query("name", description="Column to search in, default 'name'"),
                limit: int = Query(10, description="Results per page, default 10", le=100),
                page: int = Query(1, description="Page number")):
    mapper = inspect(models.PokemonData)

    # Verify column exists in the model
    if col not in mapper.columns:
        raise HTTPException(status_code=400, detail=f"Column '{col}' does not exist...")

    # Get the column type
    column_type = mapper.columns[col].type

    # Validate keyword based on the column's data type
    if keyword:
        if isinstance(column_type, Integer):
            if not keyword.isdigit():
                raise HTTPException(status_code=400, detail=f"Keyword '{keyword}' is not valid for column '{col}' (expected int)..")
            keyword = int(keyword)
        elif isinstance(column_type, Boolean):
            if keyword.lower() not in ["true", "false"]:
                raise HTTPException(status_code=400, detail=f"Keyword '{keyword}' is not valid for column '{col}' (expected bool: 'true' or 'false')..")
            keyword = keyword.lower() == "true"
        elif isinstance(column_type, String):
            if keyword.isdigit():
                raise HTTPException(status_code=400, detail=f"Keyword '{keyword}' is not valid for column '{col}' (expected string, got numeric).")
            elif keyword.lower() in ["true", "false"]:
                raise HTTPException(status_code=400, detail=f"Keyword '{keyword}' is not valid for column '{col}' (expected string, got boolean-like value).")
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported data type for column '{col}'.")

    query = db.query(models.PokemonData)

    # Perform search based on keyword
    if keyword:
        if isinstance(column_type, String):
            query = query.filter(getattr(models.PokemonData, col).ilike(f"%{keyword}%"))
        else:
            query = query.filter(getattr(models.PokemonData, col) == keyword)

    # Sorting
    if sort == "asc":
        query = query.order_by(asc(models.PokemonData.id))
    elif sort == "desc":
        query = query.order_by(desc(models.PokemonData.id))
    else:
        raise HTTPException(status_code=400, detail=f"Invalid input.. please choose ascending or descending")

    # Pagination
    offset = (page - 1) * limit
    paginated_data = query.offset(offset).limit(limit).all()

    return paginated_data
