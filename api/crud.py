import asyncio
import logging
import traceback
from datetime import datetime, UTC, timedelta

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from utils import check_product
from database import async_session
from models import Product, Supplier, Brand, TrackedProduct


async def update_tracked_products():
    while True:
        async with async_session() as session:
            current_time = datetime.now(UTC)
            try:
                sql = (
                    select(TrackedProduct.article_id, TrackedProduct.last_updated)
                    .where(TrackedProduct.is_active == True and TrackedProduct.last_updated + timedelta(minutes=30) < current_time)
                    .order_by(TrackedProduct.last_updated)
                    .limit(1)
                )
                results = await session.execute(sql)
                product = results.one_or_none()

                if product:
                    article_info = await check_product(product.article_id)
                    if isinstance(article_info, HTTPException):
                        raise f'Ошибка обновления товара {product.article}'

                    await save_product(article_info, session)
                await asyncio.sleep(1)
            except Exception:
                logging.error(traceback.format_exc())
                await asyncio.sleep(1)


async def save_product(article: dict, db: AsyncSession):
    supplier_stmt = insert(Supplier).values(
        id=article['supplierId'],
        name=article['supplier'],
        rating=article['supplierRating']
    ).on_conflict_do_update(
        index_elements=['id'],
        set_={
            'rating': article['supplierRating']
        }
    )
    await db.execute(supplier_stmt)

    brand_stmt = insert(Brand).values(
        id=article['brandId'],
        name=article['brand'],
    ).on_conflict_do_nothing()

    await db.execute(brand_stmt)

    product_stmt = insert(Product).values(
        article=article['id'],
        name=article['name'],
        price=article['priceU'] // 100,
        sale_price=article['salePriceU'] // 100 if article['salePriceU'] else None,
        sale=article['sale'] if article['sale'] else None,
        rating=article['reviewRating'],
        quantity=article['totalQuantity'],
        pics=article['pics'],
        promo=article['promoTextCard'] if article['promoTextCard'] else None,
        feedbacks=article['feedbacks'],
        supplier_id=article['supplierId'],
        brand_id=article['brandId']
    ).on_conflict_do_update(
        index_elements=['article'],
        set_={
            'name': article['name'],
            'price': article['priceU'] // 100,
            'sale_price': article['salePriceU'] // 100,
            'sale': article['sale'] if article['sale'] else None,
            'rating': article['reviewRating'],
            'quantity': article['totalQuantity'],
            'pics': article['pics'],
            'promo': article['promoTextCard'],
            'feedbacks': article['feedbacks']
        }
    )

    await db.execute(product_stmt)

    tracked_product_stmt = (
        update(TrackedProduct)
        .where(TrackedProduct.article_id == article['id'])
        .values(last_updated=datetime.now(UTC))
    )

    await db.execute(tracked_product_stmt)

    await db.commit()

    result = await db.execute(select(Product).where(Product.article == article['id']))
    return result.scalars().first()


async def tracked_product(article: int, db: AsyncSession):
    stmt = insert(TrackedProduct).values(
        article_id=article
    ).on_conflict_do_update(
        index_elements=['article_id'],
        set_={
            'is_active': True,
            'last_updated': datetime.now(UTC)
        }
    )

    await db.execute(stmt)
    await db.commit()

    result = await db.execute(select(TrackedProduct.id).where(TrackedProduct.article_id == article))
    tracked_id = result.scalars().first()
    await db.execute(update(Product).values(tracked_id=tracked_id))
