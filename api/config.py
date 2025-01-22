from datetime import timedelta, datetime, UTC

from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic_settings import BaseSettings
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer


class Settings(BaseSettings):
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int


settings = Settings()

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def verify_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get('sub')
        if username is None:
            raise HTTPException(status_code=401, detail='Неправильный токен')
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail='Неправильный токен')


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def auth_schema(token: str = Depends(oauth2_scheme)):
    username = decode_token(token)
    return username
