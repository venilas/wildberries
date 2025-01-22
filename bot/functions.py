import asyncio
import logging
import traceback
from datetime import datetime, UTC, timedelta

import aiohttp
from sqlalchemy import select
from sqlalchemy.orm import joinedload

import database
from config import settings
from models import Product, TrackedProduct


async def update_tracked_products():
    while True:
        try:
            async with database.get_session() as session:
                sql = select(TrackedProduct.article_id, TrackedProduct.last_updated).where(TrackedProduct.is_active == True).order_by(TrackedProduct.last_updated).limit(1)
                results = await session.execute(sql)
                product = results.one_or_none()

            if product:
                current_time = datetime.now(UTC)
                if product.last_updated + timedelta(minutes=5) < current_time:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            url='http://api:8000/api/v1/products/',
                            headers={
                                'Authorization': f'Bearer {settings.API_TOKEN}',
                                'Content-Type': 'application/json'
                            },
                            data={
                                'article': product.article_id
                            }
                        ) as response:
                            if response.status != 200:
                                logging.error(f'Ошибка обновления товара ({product.article_id})')
            await asyncio.sleep(1)
        except Exception:
            logging.error(traceback.format_exc())
            await asyncio.sleep(1)


async def get_num_vol_part(article: int):
    vol = 0
    part = 0
    num = 0

    if article < 1_000:
        vol = 0
        part = 0
    elif article < 100_000:
        vol = 0
        part = str(article)[:-3]
    elif article < 400_000_000:
        vol = str(article)[:-5]
        part = str(article)[:-3]

    spans = [
        14_400_000,
        28_800_000,
        43_200_000,
        72_000_000,
        100_800_000,
        106_200_000,
        111_600_000,
        117_000_000,
        131_400_000,
        160_200_000,
        165_600_000,
        192_000_000,
        204_600_000,
        219_000_000,
        240_600_000,
        262_200_000,
        283_800_000,
        305_400_000
    ]
    for ind, span in enumerate(spans, start=1):
        if article < span:
            num = ind
            break
    if not num:
        num = 19

    return str(num).zfill(2), vol, part


async def get_media(article: int, photo_num: int = 1) -> str:
    num, vol, part = await get_num_vol_part(article)
    return f'https://basket-{num}.wbbasket.ru/vol{vol}/part{part}/{article}/images/big/{photo_num}.webp'


async def get_product(article: int) -> Product | None:
    async with database.get_session() as session:
        sql_query = (
            select(Product)
            .options(joinedload(Product.supplier))
            .options(joinedload(Product.brand))
            .where(Product.article == article)
        )
        result = await session.execute(sql_query)

        return result.scalars().first()
