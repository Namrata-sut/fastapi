from typing import Optional, List
from fastapi import FastAPI, status, HTTPException, Query, Depends
from pydantic import BaseModel, Field
import requests
from sqlalchemy import asc, desc, func, inspect, Integer, Boolean, String
from sqlalchemy.orm import Session
from database import get_db
import models
from schema import (
    PokemonPostPutInputSchema,
    PokemonPatchInputSchema,
    PokemonGetOutputSchema,
    PokemonPostPatchPutOutputSchema,
    DeleteResponse,
)

app = FastAPI()


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
def get_info():
    return {"message": "Server is running"}


@app.get(
    "/pokemon/{pokemon_id}",
    response_model=PokemonGetOutputSchema,
    status_code=status.HTTP_200_OK,
)
def get_pokemon_by_id(pokemon_id: int, db: Session = Depends(get_db)):
    pokemon = db.query(models.PokemonData).filter(models.PokemonData.id == pokemon_id).first()
    if not pokemon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pokemon not found.")
    return pokemon


@app.post(
    "/pokemon",
    response_model=PokemonPostPatchPutOutputSchema,
    status_code=status.HTTP_201_CREATED,
)
def add_pokemon(pokemon: PokemonPostPutInputSchema, db: Session = Depends(get_db)):
    new_pokemon = models.PokemonData(**pokemon.dict())
    db.add(new_pokemon)
    db.commit()
    return new_pokemon


@app.put(
    "/pokemon/{pokemon_id}",
    response_model=PokemonPostPatchPutOutputSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
def update_pokemon(pokemon_id: int, pokemon: PokemonPostPutInputSchema, db: Session = Depends(get_db)):
    existing_pokemon = db.query(models.PokemonData).filter(models.PokemonData.id == pokemon_id).first()
    if not existing_pokemon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pokemon not found.")

    for key, value in pokemon.dict().items():
        setattr(existing_pokemon, key, value)

    db.commit()
    db.refresh(existing_pokemon)
    return existing_pokemon


@app.patch("/pokemon/{pokemon_id}", response_model=PokemonPostPatchPutOutputSchema)
def update_pokemon_patch(pokemon_id: int, pokemon: PokemonPatchInputSchema, db: Session = Depends(get_db)):
    existing_pokemon = db.query(models.PokemonData).filter(models.PokemonData.id == pokemon_id).first()
    if not existing_pokemon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Pokemon with id {pokemon_id} doesn't exist.")

    for key, value in pokemon.dict(exclude_unset=True).items():
        setattr(existing_pokemon, key, value)

    db.commit()
    db.refresh(existing_pokemon)
    return existing_pokemon


@app.delete("/pokemon/{pokemon_id}", response_model=DeleteResponse, status_code=200)
def delete_pokemon(pokemon_id: int, db: Session = Depends(get_db)):
    if not isinstance(pokemon_id, int):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pokemon ID must be a valid integer.",
        )

    existing_pokemon = db.query(models.PokemonData).filter(models.PokemonData.id == pokemon_id).first()
    if not existing_pokemon:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pokemon not found.")

    db.delete(existing_pokemon)
    db.commit()
    return {"message": "Pokemon deleted successfully."}


@app.post("/pokemon/fetch_and_store/")
def fetch_and_store(db: Session = Depends(get_db)):
    response = requests.get("https://coralvanda.github.io/pokemon_data.json")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch data.")

    data = response.json()
    pokemon_data = [
        {
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
            "legendary": pokemon["Legendary"],
        }
        for pokemon in data
    ]

    try:
        # Perform bulk insert using bulk_insert_mappings
        db.bulk_insert_mappings(models.PokemonData, pokemon_data)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
    return {"message": "Data successfully stored in the database"}


@app.get(
    "/pokemon/",
    response_model=List[PokemonGetOutputSchema],
    status_code=status.HTTP_200_OK,
)
def get_pokemon(
        sort: str = Query("asc", description="Sort order: 'asc' or 'desc'"),
        keyword: Optional[str] = Query(None, description="Search keyword"),
        col: str = Query("name", description="Column to search in, default 'name'"),
        limit: int = Query(10, description="Results per page, default 10", le=100),
        page: int = Query(1, description="Page number"),
        db: Session = Depends(get_db)
):
    mapper = inspect(models.PokemonData)

    # Verify column exists in the model
    if col not in mapper.columns:
        raise HTTPException(status_code=400, detail=f"Column '{col}' does not exist...")

    # Get the column type
    column_type = mapper.columns[col].type

    # Validate keyword based on the column's data type
    if keyword:
        if isinstance(column_type, Integer) and not keyword.isdigit():
            raise HTTPException(
                status_code=400,
                detail=f"Keyword '{keyword}' is not valid for column '{col}' (expected int)."
            )
        elif isinstance(column_type, Boolean) and keyword.lower() not in ["true", "false"]:
            raise HTTPException(status_code=400,
                                detail=f"Keyword '{keyword}' is not valid for column '{col}' (expected bool: 'true' or 'false').")
        elif isinstance(column_type, String) and keyword.isdigit():
            raise HTTPException(status_code=400,
                                detail=f"Keyword '{keyword}' is not valid for column '{col}' (expected string).")

    query = db.query(models.PokemonData)

    # Perform search based on keyword
    if keyword:
        if isinstance(column_type, String):
            query = query.filter(getattr(models.PokemonData, col).ilike(f"%{keyword}%"))
        else:
            query = query.filter(getattr(models.PokemonData, col) == keyword)

    # Sorting
    if sort == "asc":
        query = query.order_by(asc(getattr(models.PokemonData, col)))
    elif sort == "desc":
        query = query.order_by(desc(getattr(models.PokemonData, col)))
    else:
        raise HTTPException(status_code=400, detail="Invalid sort order. Use 'asc' or 'desc'.")

    # Pagination
    offset = (page - 1) * limit
    paginated_data = query.offset(offset).limit(limit).all()

    return paginated_data
