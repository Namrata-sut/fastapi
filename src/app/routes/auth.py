import os
from datetime import datetime, timedelta
from typing import Annotated, List

from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from src.app.database.database import get_db
from src.app.models.models import Users, UserRole

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret_key")
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


class CreateUserRequest(BaseModel):
    username: str
    password: str
    role: UserRole = UserRole.user  # Default role


class Token(BaseModel):
    access_token: str
    token_type: str
    role: UserRole  # Include role in token response


class UserResponse(BaseModel):
    id: int
    username: str
    role: UserRole

    class Config:
        orm_mode = True


db_dependency = Annotated[Session, Depends(get_db)]


def get_user_by_username(db: Session, username: str):
    return db.query(Users).filter(Users.username == username).first()


@router.post("/user", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = Users(
        username=create_user_request.username,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        role=create_user_request.role
    )
    db_user = get_user_by_username(db, create_user_model.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)
    user_response = UserResponse(
        id=create_user_model.id,
        username=create_user_model.username,
        role=create_user_model.role
    )

    return user_response


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    print(f"Token generated: {token}")
    return {'access_token': token, 'token_type': 'bearer', 'role': user.role}


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    print(user)
    if not user or not bcrypt_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Could not validate users")
    print(f"User retrieved: {user}")
    return user


def create_access_token(username: str, user_id: int, role: UserRole, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role.value}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if not username or not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate userss.")
        return {'username': username, 'id': user_id, 'role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could now validate the usersss..")


def get_current_user_role(current_user: dict = Depends(get_current_user)):
    return UserRole(current_user.get('role'))


def RoleChecker(allowed_roles: List[UserRole]):
    async def check_role(role: UserRole = Depends(get_current_user_role)):
        if role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted...")
    return check_role
