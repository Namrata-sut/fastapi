from datetime import timedelta, datetime
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import Users, UserRole
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

from database import get_db

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRETE_KEY = "ahp9348rh24903hrf23tfg2894tpg34pgh4g4gyes45yh5sej5jjjjts"
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


@router.post("/user", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = Users(
        username=create_user_request.username,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        role=create_user_request.role
    )
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
    return {'access_token': token, 'token_type': 'bearer', 'role': user.role}


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, role: UserRole, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role.value}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRETE_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRETE_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")
        return {'username': username, 'id': user_id, 'role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could now validate the user..")


def get_current_user_role(current_user: dict = Depends(get_current_user)):
    return UserRole(current_user.get('role'))


def RoleChecker(allowed_roles: List[UserRole]):
    async def check_role(role: UserRole = Depends(get_current_user_role)):
        if role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Operation not permitted...")

    return check_role
