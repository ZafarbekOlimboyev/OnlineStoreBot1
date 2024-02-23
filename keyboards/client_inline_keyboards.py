from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import DB_NAME
from utils.database import Database


db = Database(DB_NAME)


# Function for make inline keyboards from category names
def get_category_list() -> InlineKeyboardMarkup:
    categories = db.get_categories()
    rows = []
    for category in categories:
        rows.append([
            InlineKeyboardButton(
                text=category[1],
                callback_data=str(category[0])
            )
        ])
    kb_categories = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb_categories


# Function for make inline keyboards from product names
def get_product_list(cat_id: int) -> InlineKeyboardMarkup:
    products = db.get_products(cat_id)
    rows = []
    for product in products:
        rows.append([
            InlineKeyboardButton(
                text=product[1],
                callback_data=str(product[0])
            )
        ])
    kb_products = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb_products
def left_right(file_id: str):
    left_right1 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️", callback_data=f"l{file_id}"),InlineKeyboardButton(text="➡️",callback_data=f"r{file_id}")]
    ])
    return left_right1

def del_left_right(file_id: str):
    left_right1 = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="This ad",callback_data=f"{file_id}")],
        [InlineKeyboardButton(text="⬅️", callback_data=f"l{file_id}"),InlineKeyboardButton(text="➡️",callback_data=f"r{file_id}")]
    ])
    return left_right1
def del_left_righ(file_id: str):
    left_right1 = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="This ad",callback_data=f"{file_id}")]
    ])
    return left_right1
