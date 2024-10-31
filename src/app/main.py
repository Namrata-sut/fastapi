from fastapi import FastAPI

from src.app.routes import auth, pokemon

# Create the FastAPI app
app = FastAPI()

# Include the routers from the different route modules
app.include_router(auth.router)    # Include the auth routes
app.include_router(pokemon.router)  # Include the pokemon routes
