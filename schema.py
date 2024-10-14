from pydantic import BaseModel, Field
from typing import Optional, List


# Base schema for Pydantic models
class OurBaseModel(BaseModel):
    class Config:
        from_attributes = True


# Input Schemas
class PokemonPostPutInputSchema(BaseModel):
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


class PokemonPatchInputSchema(BaseModel):
    name: Optional[str] = Field(min_length=5, max_length=30)
    type_1: Optional[str]
    type_2: Optional[str] = None
    total: Optional[int]
    hp: Optional[int]
    attack: Optional[int]
    defense: Optional[int]
    sp_atk: Optional[int]
    sp_def: Optional[int]
    speed: Optional[int] = Field(lt=500, gt=100)
    generation: Optional[int] = Field(default=2)
    legendary: Optional[bool]


# Output Schemas
class PokemonGetOutputSchema(BaseModel):
    id: int
    name: str
    type_1: str
    type_2: Optional[str]
    total: int
    hp: int
    attack: int
    defense: int
    sp_atk: int
    sp_def: int
    speed: int
    generation: int
    legendary: bool


class DeleteResponse(BaseModel):
    message: str


class PokemonGetAllOutputSchema(List[PokemonGetOutputSchema]):
    pass


class PokemonPostPatchPutOutputSchema(PokemonGetOutputSchema):
    pass
