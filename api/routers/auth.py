from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from config import verify_password, create_access_token

router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


class UserLogin(BaseModel):
    username: str
    password: str


fake_user = {
    'test': {
        'hashed_password': '$2b$12$wEAmWbUzYnbzNojxePEHsec.0i8k6lb.5.UivvggaUfsPYukt36cW'
    }
}


@router.post('/token', response_model=Token)
async def login(payload: UserLogin):
    user = fake_user.get(payload.username)
    if not user or not verify_password(payload.password, user['hashed_password']):
        raise HTTPException(status_code=401, detail='Неверный данные')

    access_token = create_access_token(data={'sub': payload.username})
    return {'access_token': access_token, 'token_type': "bearer"}
