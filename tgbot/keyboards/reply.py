from aiogram.types import ReplyKeyboardMarkup, KeyboardButton



main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [   KeyboardButton(text='Показать все ссылки'), 
            KeyboardButton(text='Добавить ссылки'), 
            KeyboardButton(text='Удалить ссылки')
        ]
    ], 
    resize_keyboard=True,
    input_field_placeholder='Выберите категорию'
)


category_kb = ReplyKeyboardMarkup(
    keyboard=[
        [   KeyboardButton(text='Работа'), 
            KeyboardButton(text='Школа'), 
            KeyboardButton(text='Личное'),
            KeyboardButton(text='Разное')
        ]
    ], 
    resize_keyboard=True, 
    input_field_placeholder='Выберите категорию'
)


priority_kb = ReplyKeyboardMarkup(
    keyboard=[
        [   KeyboardButton(text='🟢 Низкий'), 
            KeyboardButton(text='🟡 Средний'), 
            KeyboardButton(text='🔴 Высокий'),
        ]
    ], 
    resize_keyboard=True, 
    input_field_placeholder='Выберите категорию'
)



select_kb = ReplyKeyboardMarkup(
    keyboard=[
        [   KeyboardButton(text='Добавить все'), 
            KeyboardButton(text='Выбрать ссылки'), 
        ]
    ], 
    resize_keyboard=True, 
    input_field_placeholder='Выберите категорию'
)