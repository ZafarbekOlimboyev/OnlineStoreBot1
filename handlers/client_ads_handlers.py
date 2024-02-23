from time import time

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from config import DB_NAME, admins
from functions.show_ad import next_ad, back_ad, this_ad
from keyboards.client_inline_keyboards import get_category_list, get_product_list, left_right, del_left_right, \
    del_left_righ
from states.client_states import ClientAdsStates
from utils.database import Database
from utils.my_commands import commands_user

ads_router = Router()
db = Database(DB_NAME)

#
# @ads_router.message(F.photo)
# async def test(message: Message, album: list(Message)):
#     print(album)


@ads_router.message(Command('new_ad'))
async def new_ad_handler(message: Message, state: FSMContext):
    await state.set_state(ClientAdsStates.selectAdCategory)
    await message.answer(
        "Please, choose a category for your ad: ",
        reply_markup=get_category_list()
    )


@ads_router.callback_query(ClientAdsStates.selectAdCategory)
async def select_ad_category(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ClientAdsStates.selectAdProduct)
    await callback.message.edit_text(
        "Please, choose a product type for your ad: ",
        reply_markup=get_product_list(int(callback.data))
    )


@ads_router.callback_query(ClientAdsStates.selectAdProduct)
async def select_ad_product(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ClientAdsStates.insertTitle)
    await state.update_data(ad_product=callback.data)
    await callback.message.answer(
        f"Please, send title for your ad!\n\n"
        f"For example:"
        f"\n\t- iPhone 15 Pro Max 8/256 is on sale"
        f"\n\t- Macbook Pro 13\" M1 8/256 is on sale"
    )
    await callback.message.delete()


@ads_router.message(ClientAdsStates.insertTitle)
async def ad_title_handler(message: Message, state: FSMContext):
    await state.update_data(ad_title=message.text)
    await state.set_state(ClientAdsStates.insertText)
    await message.answer("OK, please, send text(full description) for your ad.")


@ads_router.message(ClientAdsStates.insertText)
async def ad_text_handler(message: Message, state: FSMContext):
    await state.update_data(ad_text=message.text)
    await state.set_state(ClientAdsStates.insertPrice)
    await message.answer("OK, please, send price for your ad (only digits).")


@ads_router.message(ClientAdsStates.insertPrice)
async def ad_price_handler(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(ad_price=int(message.text))
        await state.set_state(ClientAdsStates.insertImages)
        await message.answer("OK, please, send image(s) for your ad.")
    else:
        await message.answer("Please, send only number...")


@ads_router.message(ClientAdsStates.insertImages)
async def ad_photo_handler(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data(ad_photo=message.photo[-1].file_id)
        await state.set_state(ClientAdsStates.insertPhone)
        await message.answer("OK, please, send phone number for contact with your.")
    else:
        await message.answer("Please, send image(s)...")


@ads_router.message(ClientAdsStates.insertPhone)
async def ad_phone_handler(message: Message, state: FSMContext):
    await state.update_data(ad_phone=message.text)
    all_data = await state.get_data()
    try:
        x = db.insert_ad(
            title=all_data.get('ad_title'),
            text=all_data.get('ad_text'),
            price=all_data.get('ad_price'),
            image=all_data.get('ad_photo'),
            phone=all_data.get('ad_phone'),
            u_id=message.from_user.id,
            prod_id=all_data.get('ad_product'),
            date=time()
        )
        if x:
            await state.clear()
            await message.answer("Your ad successfully added!")
        else:
            await message.answer("Something error, please, try again later...")
    except:
        await message.answer("Resend phone please...")

#----------------------- HOME WORK -------------------------------------------#

#-----------------------Command ads----------------------------------------#
#_______________________START______________________________________________#
@ads_router.message(Command('ads'))
async def ads_list_handler(message: Message, state: FSMContext):
    await state.set_state(ClientAdsStates.show_ad)
    my_ads = db.get_my_ads(message.from_user.id)
    my_ads = list(my_ads)
    count_ad = len(my_ads)
    # print(message.from_user.id)
    if count_ad == 0:
        await message.answer(text="You have not any ads")
    elif count_ad == 1:
        ad = my_ads[0]
        await message.answer_photo(
            photo=ad[4],
            caption=f"<b>{ad[1]}</b>\n\n{ad[2]}\n\nPrice: ${ad[3]}",
            parse_mode=ParseMode.HTML
        )
    else:
        ad = my_ads[0]
        keyboard = left_right(ad[4][:63])
        await message.answer_photo(
            photo=ad[4],
            caption=f"<b>{ad[1]}</b>\n\n{ad[2]}\n\nPrice: ${ad[3]}",
            parse_mode=ParseMode.HTML,reply_markup=keyboard
        )

#----------------------------------------------------------------------------------#

@ads_router.callback_query(ClientAdsStates.show_ad)
async def left_right_(query: CallbackQuery):
    if query.data[0] == "r":
        my_ads = db.info_ad(next_ad(file_id=query.data[1:],u_id=query.from_user.id))
        if my_ads:
            ad = my_ads
            keyboard = left_right(ad[4][:63])
            await query.message.delete()
            await query.message.answer_photo(
                photo=ad[4],
                caption=f"<b>{ad[1]}</b>\n\n{ad[2]}\n\nPrice: ${ad[3]}",
                parse_mode=ParseMode.HTML, reply_markup=keyboard
            )
        else:
            await query.answer(text="finish")
    elif query.data[0] == "l":
        my_ads = db.info_ad(back_ad(file_id=query.data[1:], u_id=query.from_user.id))
        if my_ads:
            ad = my_ads
            keyboard = left_right(ad[4][:63])
            await query.message.delete()
            await query.message.answer_photo(
                photo=ad[4],
                caption=f"<b>{ad[1]}</b>\n\n{ad[2]}\n\nPrice: ${ad[3]}",
                parse_mode=ParseMode.HTML, reply_markup=keyboard
            )
        else:
            await query.answer("finished")
#-------------------FINISH-----------------------------------------------------#

#-------------------- Command del_ad-------------------------------------------#
@ads_router.message(Command("del_ad"))
async def del_ad(msg: Message, state: FSMContext):
    await state.set_state(ClientAdsStates.del_ad)
    my_ads = db.get_my_ads(msg.from_user.id)
    my_ads = list(my_ads)
    count_ad = len(my_ads)
    # print(message.from_user.id)
    if count_ad == 0:
        await msg.answer(text="You have not any ads")
    elif count_ad == 1:
        ad = my_ads[0]
        await msg.answer_photo(
            photo=ad[4],
            caption=f"<b>{ad[1]}</b>\n\n{ad[2]}\n\nPrice: ${ad[3]}",
            parse_mode=ParseMode.HTML,reply_markup=del_left_righ(ad[4][:63])
        )
    else:
        ad = my_ads[0]
        keyboard = del_left_right(ad[4][:63])
        await msg.answer_photo(
            photo=ad[4],
            caption=f"<b>{ad[1]}</b>\n\n{ad[2]}\n\nPrice: ${ad[3]}",
            parse_mode=ParseMode.HTML, reply_markup=keyboard
        )
@ads_router.callback_query(ClientAdsStates.del_ad)
async def del_ad1(query: CallbackQuery,state: FSMContext):
    if query.data[0] == "r":
        my_ads = db.info_ad(next_ad(file_id=query.data[1:],u_id=query.from_user.id))
        if my_ads:
            ad = my_ads
            keyboard = del_left_right(ad[4][:63])
            await query.message.delete()
            await query.message.answer_photo(
                photo=ad[4],
                caption=f"<b>{ad[1]}</b>\n\n{ad[2]}\n\nPrice: ${ad[3]}",
                parse_mode=ParseMode.HTML, reply_markup=keyboard
            )
        else:
            await query.answer(text="finish")
    elif query.data[0] == "l":
        my_ads = db.info_ad(back_ad(file_id=query.data[1:], u_id=query.from_user.id))
        if my_ads:
            ad = my_ads
            keyboard = del_left_right(ad[4][:63])
            await query.message.delete()
            await query.message.answer_photo(
                photo=ad[4],
                caption=f"<b>{ad[1]}</b>\n\n{ad[2]}\n\nPrice: ${ad[3]}",
                parse_mode=ParseMode.HTML, reply_markup=keyboard
            )
        else:
            await query.answer("finished")
    else:
        # print(this_ad(query.data[1:],u_id=query.from_user.id))
        db.del_ad_with_img(this_ad(query.data[1:],u_id=query.from_user.id))
        await query.message.delete()
        await query.answer("Deleted")
        await query.message.answer("Deleted")
        await state.clear()