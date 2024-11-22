import os 
import string 
from aiogram import Router, types, F
from aiogram.filters import Command, or_f, StateFilter
from aiogram.fsm.context import FSMContext
from notion_client import AsyncClient 

from database.query import save_to_database, delete_from_database
from keyboards.reply import main_kb, category_kb, priority_kb, select_kb
from notion import get_db_rows, add_data, safe_get
from filters.filter import CommaSeparatedDigitsFilter
from states.add_data import AddData 
from states.remove_data import RemoveData 
from utils.utils import (
    get_page_title, 
    extract_urls, 
    get_output_for_user, 
    get_url_to_html,
    get_time

)

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())



router = Router()
client= AsyncClient(auth=os.getenv('NOTION_TOKEN'))
database_id = os.getenv('DATABASE_ID')



@router.message(Command("start"))
async def start_command_handler(message: types.Message):
    from_user = message.from_user
    greeting_text = f"С возвращением, {from_user.full_name}! Чем могу помочь?"
    await message.answer(greeting_text, reply_markup=main_kb)

    
@router.message(F.text == "Показать все ссылки")
async def get_urls(message: types.Message):
    data = await get_db_rows(os.getenv('DATABASE_ID'))
    await message.answer("Вот данные, сохраненные в Notion:", 
                         reply_markup=main_kb, 
                         disable_web_page_preview=True)

    for row in data['results']:
        title = safe_get(row, 'properties.Title.title.0.text.content')
        url = safe_get(row, 'properties.URL.url')
        category = safe_get(row, 'properties.Category.select.name')
        priority = safe_get(row, 'properties.Priority.select.name')
        timestamp = safe_get(row, 'properties.Timestamp.date.start') 
        text = get_output_for_user(title, url, category, priority, timestamp)
        await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)
    

@router.message(StateFilter(None), F.text == "Удалить ссылки")
async def update_urls(message: types.Message, state: FSMContext):
    await message.answer("Введите через запятую нoмера ссылок, которые вы хотите удалить. Например: 1,2,3 и т.д.", 
                         reply_markup=types.ReplyKeyboardRemove()) 
    
    data = await get_db_rows(os.getenv('DATABASE_ID'))
    for i, row in enumerate(data['results']):
        title = safe_get(row, 'properties.Title.title.0.text.content')
        url = safe_get(row, 'properties.URL.url')
        text = (
            f"{i+1}. Title: <b>{title}</b>\n"
            f"URL: {url}\n"
        ) 
        await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)
    await state.set_state(RemoveData.url)



@router.message(RemoveData.url, CommaSeparatedDigitsFilter())
async def delete_urls(message: types.Message, state: FSMContext):
    nums = message.text.split(",")
    data = await get_db_rows(os.getenv('DATABASE_ID'))
    for num in nums: 
        index = int(num)-1
        row = data['results'][index]
    
        # delete db row in Notion
        page_id = row['id']
        await client.pages.update(
            page_id=page_id,
            archived=True
        )

        # delete record in local db
        title = safe_get(row, 'properties.Title.title.0.text.content') 
        await delete_from_database(title)

    await message.answer("Данные были удалены из Notion.", reply_markup=main_kb)
    await state.clear()



@router.message(StateFilter(None), F.text == "Добавить ссылки")
async def add_cmd(message: types.Message, state: FSMContext):
    await message.answer("Введите ссылки, которые вы хотели бы сохранить", 
                         reply_markup=types.ReplyKeyboardRemove()) 
    await state.set_state(AddData.url)



@router.message(AddData.url, or_f(F.text == 'Добавить все', F.text == 'Выбрать ссылки'))
async def add_all_or_select_url(message: types.Message, state: FSMContext):
    curr_data = await state.get_data()

    if message.text == "Добавить все": 
        await message.answer(f"Выберите «категорию» для ссылки: {curr_data['url'][0]}",
                            disable_web_page_preview=True,
                            reply_markup=category_kb)
        await state.set_state(AddData.category) 

    elif message.text == "Выбрать ссылки":
        urls = curr_data.get('url', []) 
        text = get_url_to_html(urls)
        await message.answer("Введите через запятую нoмера ссылок, которые вы хотите добавить в Notion. Например: 1,2,3 и т.д.") 
        await message.answer(text, parse_mode="HTML", disable_web_page_preview=True, 
                             reply_markup=types.ReplyKeyboardRemove())



@router.message(AddData.url, CommaSeparatedDigitsFilter())
async def add_all_or_select_url2(message: types.Message, state: FSMContext):

    curr_data = await state.get_data()
    curr_urls = curr_data.get('url', [])
    nums = message.text.split(",")
    urls = []
    for num in nums: 
        index = (int(num) - 1)
        urls.append(curr_urls[index])
    await state.update_data(url=urls)

    updated_data = await state.get_data()
    await message.answer(f"Выберите «категорию» для ссылки: {updated_data['url'][0]}",
                         disable_web_page_preview=True,
                         reply_markup=category_kb)
    await state.set_state(AddData.category)



@router.message(AddData.url, F.text)
async def add_url(message: types.Message, state: FSMContext):
    urls = extract_urls(message.text)
    await state.update_data(url = urls)
    curr_data = await state.get_data()
    await message.answer("Хотите ли вы добавить эти ссылки или выбрать конкретные ссылки для добавления?", 
                         reply_markup=select_kb) 



@router.message(AddData.category, F.text)
async def add_category(message: types.Message, state: FSMContext):
    curr_data = await state.get_data()
    urls = curr_data.get("url", [])
    categories = curr_data.get("category", [])
    categories.append(message.text)
    await state.update_data(category=categories)

    if len(categories) < len(urls):
        next_url = urls[len(categories)]  
        await message.answer(f"Выберите «категорию» для ссылки: {next_url}", 
                             disable_web_page_preview=True,
                             reply_markup=category_kb)
    else:
        await message.answer("Все категории введены!", 
                             reply_markup=types.ReplyKeyboardRemove())
        await message.answer(f"Теперь введите уровень «приоритета» для ссылки: {urls[0]}",
                             disable_web_page_preview=True,
                             reply_markup=priority_kb)
        await state.set_state(AddData.priority)



@router.message(AddData.priority, F.text)
async def add_priority(message: types.Message, state: FSMContext):
    curr_data = await state.get_data()
    urls = curr_data.get("url", [])
    priority = curr_data.get("priority", [])
    priority.append(message.text)
    await state.update_data(priority=priority)

    if len(priority) < len(urls):
        next_url = urls[len(priority)]  
        await message.answer(f"Введите уровень «приоритета» для ссылки.k: {next_url}",
                             disable_web_page_preview=True,
                             reply_markup=priority_kb)
    elif len(priority) == len(urls): 
        await message.answer("Все приоритеты введены!", 
                             reply_markup=types.ReplyKeyboardRemove())
        data = await state.get_data()

        # display data to user 
        await message.answer("Вот данные, которые я сохраню в Notion: ")
        for i in range(len(data['url'])): 
            url = data['url'][i].rstrip(string.punctuation)
            title = await get_page_title(url)
            category = data['category'][i]
            priority = data['priority'][i]
            timestamp = get_time(message)
            # save to notion db
            await add_data(client, database_id, url, title, category, priority, timestamp)
            # save to local db 
            time = str(timestamp).split("T")[0]
            await save_to_database(title, url, category, priority, time)
            # log to user 
            text = get_output_for_user(title, url, category, priority, timestamp)
            await message.answer(text, parse_mode="HTML", disable_web_page_preview=True,
                                 reply_markup=main_kb) 
            await state.clear()
            

