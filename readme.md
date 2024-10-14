## Installation and Setup

### Requirements

- Python 3.9+
- PostgreSQL

### Installation

1. Clone the repository:

   ```bash
    https://github.com/Namrata-sut/fastapi.git
    pip install -r requirements.txt

# pokemon API

A FastAPI-based API to manage pokemon data, including CRUD operations, searching, sorting, and bulk data insertion from an external API.

## Features

- **CRUD operations**: Create, Read, Update, and Delete pokemon records.
- **Search**: Search Pokemon data by keyword in a specified column.
- **Sorting**: Sort pokemon data in ascending or descending order.
- **Pagination**: Fetch Pokemon data with customizable limit and pagination.
- **Bulk data insertion**: Fetch pokemon data from an external API and store it in the database.

## Endpoints

### Health Check

- **GET** `/test`: Check if the server is running.

### pokemon Data Operations

- **GET** `/pokemon/{pokemon_id}`: Fetch pokemon details by ID.
  - Path Parameter:
    - `pokemon_id`: (integer) pokemon ID.
  - Response: Returns details of the pokemon or raises an error if not found.

- **POST** `/pokemon`: Add a new pokemon.
  - Body:
    - JSON object conforming to the `PokemonPostPutInputSchema`.
  - Response: Returns the newly added pokemon.

- **PUT** `/pokemon/{pokemon_id}`: Update an existing pokemon by ID.
  - Path Parameter:
    - `pokemon_id`: (integer) pokemon ID.
  - Body:
    - JSON object conforming to the `PokemonPostPutInputSchema`.
  - Response: Returns the updated pokemon.

- **PATCH** `/pokemon/{pokemon_id}`: Partially update a pokemon by ID.
  - Path Parameter:
    - `pokemon_id`: (integer) pokemon ID.
  - Body:
    - JSON object conforming to the `PokemonPatchInputSchema`.
  - Response: Returns the updated pokemon.

- **DELETE** `/pokemon/{pokemon_id}`: Delete a pokemon by ID.
  - Path Parameter:
    - `pokemon_id`: (integer) pokemon ID.
  - Response: A confirmation message if successful.

### Fetch and Store pokemon Data

- **POST** `/pokemon/fetch_and_store/`: Fetch pokemon data from an external API and store it in the database.
  - Response: A confirmation message if data is successfully stored.

### List pokemon with Search, Sort, and Pagination

- **GET** `/pokemon/`: Get a list of pokemon with optional search, sort, and pagination.
  - Query Parameters:
    - `sort`: (string) Sort order: 'asc' or 'desc' (default: 'asc').
    - `keyword`: (string, optional) Search keyword to filter results.
    - `col`: (string, optional) Column to search in (default: 'name').
    - `limit`: (integer, optional) Number of results per page (default: 10).
    - `page`: (integer, optional) Page number to fetch (default: 1).

## Schemas

### PokemonPostPutInputSchema

- `name`: (string) Name of the pokemon.
- `type_1`: (string) Primary type of the pokemon.
- `type_2`: (string, optional) Secondary type of the pokemon.
- `total`: (integer) Total
- `hp`: (integer) 
- `attack`: (integer) Attack 
- `defense`: (integer) Defense 
- `sp_atk`: (integer) Special attack 
- `sp_def`: (integer) Special defense
- `speed`: (integer) Speed 
- `generation`: (integer) Generation 
- `legendary`: (boolean) Whether the pokemon is legendary or not.

### PokemonPatchInputSchema

- Allows partial updates for the following fields:
  - `name`, `type_1`, `type_2`, `total`, `hp`, `attack`, `defense`, `sp_atk`, `sp_def`, `speed`, `generation`, `legendary`.
