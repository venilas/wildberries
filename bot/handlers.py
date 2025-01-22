from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InputMediaPhoto

import functions
import keyboards
from states import UserForm

router = Router()


@router.message(CommandStart())
async def welcome(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        'Добро пожаловать! Здесь вы можете узнать актуальные данные по товару <b>Wildberries</b>',
        reply_markup=keyboards.menu()
    )


@router.message(F.text == 'Получить данные по товару')
async def wait_article(message: Message, state: FSMContext):
    await state.clear()

    await message.answer('Пришлите артикул товара')
    await state.set_state(UserForm.article)


@router.message(F.text, UserForm.article)
async def article_valid(message: Message, state: FSMContext):
    article = message.text

    if article.isdigit():
        await state.clear()
        product = await functions.get_product(int(article))
        if product:
            if product.promo:
                promo_text = f'Акция: <b>{product.promo}</b>\n'
            else:
                promo_text = ''

            if product.sale_price:
                price = f' <b>{product.sale_price}</b> <s>{product.price}</s> ({product.sale}%)\n'
            else:
                price = f'<b>{product.price}</b>\n'

            caption = (
                f'Артикул: <code>{product.article}</code>\n'
                f'Название: <a href="https://www.wildberries.ru/catalog/{product.article}/detail.aspx">{product.name}</a> ({product.rating})\n'
                f'\n'
                f'Продавец: <b><a href="https://www.wildberries.ru/seller/{product.supplier.id}">{product.supplier.name}</a></b> ({product.supplier.rating} <i>рейтинг</i>)\n'
                f'Бренд: <b><a href="https://www.wildberries.ru/brands/{product.brand.id}">{product.brand.name}</a></b>\n'
                f'\n'
                f'{promo_text}'
                f'Цена: {price}'
                f'Кол-во товаров: <b>{product.quantity}</b>\n'
                f'Кол-во отзывов: <b>{product.feedbacks}</b>'
            )

            if product.pics:
                if product.pics > 1:
                    media = [
                        InputMediaPhoto(
                            media=await functions.get_media(int(article), photo_num),
                            caption=caption if photo_num == 1 else None
                        ) for photo_num in range(1, product.pics + 1)
                    ]
                    await message.answer_media_group(media=media[:5])
                else:
                    await message.answer_photo(
                        photo=await functions.get_media(int(article)),
                        caption=caption
                    )
            else:
                await message.answer(caption)
        else:
            await message.answer('Данного товара нет в нашей базе', reply_markup=keyboards.menu())

    else:
        await message.answer('Пришлите только артикул\n\n<b><i>Пример: 216531727</i></b>')
