from aiogram.fsm.state import State, StatesGroup


class ClientAdsStates(StatesGroup):
    selectAdCategory = State()
    selectAdProduct = State()
    insertTitle = State()
    insertText = State()
    insertPrice = State()
    insertImages = State()
    insertPhone = State()
    show_ad = State()
    del_ad = State()