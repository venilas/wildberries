import aiohttp
from fastapi import HTTPException


async def check_product(article: int) -> dict | HTTPException:
    async with aiohttp.ClientSession() as session:
        async with session.get(
                url='https://card.wb.ru/cards/v1/detail',
                params={
                    'appType': 1,
                    'curr': 'rub',
                    'dest': -1257786,
                    'spp': 30,
                    'nm': article
                }
        ) as response:
            if response.status == 200:
                data = await response.json()
                if data['data']['products']:
                    return data['data']['products'][0]
                else:
                    return HTTPException(status_code=404, detail='Товара с таким артикулом не существует')
            else:
                return HTTPException(status_code=response.status, detail=await response.text())
