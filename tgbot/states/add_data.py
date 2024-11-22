from aiogram.fsm.state import StatesGroup, State

class AddData(StatesGroup): 
    url = State()
    category = State()
    priority = State()