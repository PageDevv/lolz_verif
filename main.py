import asyncio

import aiogram
from aiogram import types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import F

import configparser

import kb
import db


class NewNote(StatesGroup):
    title = State()
    text_note = State()


class FindNote(StatesGroup):
    phrase = State()


config = configparser.ConfigParser()
config.read("config.ini")

token = config.get("bot", "token")

bot = aiogram.Bot(token=token)
storage = MemoryStorage()
dp = aiogram.Dispatcher(storage=storage)

db.check_db()


@dp.callback_query(F.data == "back")
@dp.message(F.text == "/start")
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    db.add_user_to_db(message.from_user.id)
    await bot.send_message(message.from_user.id,
                           f"Привет! Я бот для заметок. Нажимай на кнопки чтобы работать со мной.",
                           reply_markup=kb.main_kb())


@dp.callback_query(F.data == 'create_note')
async def create_note(message: types.Message, state: FSMContext):
    await state.clear()
    await bot.send_message(message.from_user.id,
                           "Введите название заметки", reply_markup=kb.back_kb())
    await state.set_state(NewNote.title)


@dp.message(NewNote.title)
async def title_note(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await bot.send_message(message.from_user.id,
                           "Введите текст заметки", reply_markup=kb.back_kb())
    await state.set_state(NewNote.text_note)


@dp.message(NewNote.text_note)
async def text_note(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    data = await state.get_data()
    db.add_note_to_db(message.from_user.id, data['title'], data['text'])
    await bot.send_message(message.from_user.id,
                           f"Заметка <b>{data['title']}</b> добавлена", reply_markup=kb.main_kb(), parse_mode="HTML")
    await state.clear()


@dp.callback_query(F.data == 'all_notes')
async def all_notes(message: types.Message, state: FSMContext):
    await state.set_state("all_notes")
    user_id = message.from_user.id
    row = db.get_all_notes(user_id)
    await state.update_data(row=row)

    if row:
        await bot.send_message(user_id,
                               f"Вот все ваши заметки:", reply_markup=kb.get_notes(db.get_all_notes(user_id), 0))
    else:
        await bot.send_message(user_id, "Заметок нет.", reply_markup=kb.main_kb())


@dp.callback_query(F.data.startswith("prev_page:"))
async def prev_page(call: aiogram.types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = await state.get_data()
    row = data['row']
    user_id = call.from_user.id
    page = int(call.data.split(":")[1])
    page -= 1
    print(await state.get_state())
    await bot.send_message(user_id, "Вот все ваши заметки:", reply_markup=kb.get_notes(row, page))


@dp.callback_query(F.data.startswith("next_page:"))
async def next_page(call: aiogram.types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = await state.get_data()
    row = data['row']
    user_id = call.from_user.id
    page = int(call.data.split(":")[1])
    page += 1
    await bot.send_message(user_id, "Вот все ваши заметки:", reply_markup=kb.get_notes(row, page))


@dp.callback_query(F.data.startswith("note_"))
async def show_note(call: aiogram.types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    note_id = call.data.split("_")[1]
    note = db.get_note(note_id)
    await bot.send_message(call.from_user.id,
                           f"Заметка <b>{note[2]}</b>: \n\n{note[3]} \n\n#id{note_id}", reply_markup=kb.open_note(), parse_mode="HTML")


@dp.callback_query(F.data == "delete_note")
async def delete_note(call: aiogram.types.CallbackQuery, state):
    await call.message.delete()
    note_id = call.message.text.split("#id")[1]
    note = db.get_note(note_id)
    db.delete_note(note_id)
    await bot.send_message(call.from_user.id, f"Заметка <b>{note[2]}</b> удалена.", reply_markup=kb.main_kb(), parse_mode="HTML")
    await state.set_state("delete_note")


@dp.callback_query(F.data == "find_note")
async def find_note(message: types.Message, state: FSMContext):
    await state.clear()
    await bot.send_message(message.from_user.id, "🔍 Введите ключевое слово или фразу для поиска.", reply_markup=kb.back_kb())
    await state.set_state(FindNote.phrase)


@dp.message(FindNote.phrase)
async def find_note(message: types.Message, state: FSMContext):
    row = db.find_note(message.from_user.id, message.text)
    await state.update_data(row=row)
    if row:
        await bot.send_message(message.from_user.id,
                               f"Все заметки с этим ключевым словом:", reply_markup=kb.get_notes(row, 0))

    else:
        await bot.send_message(message.from_user.id, "Заметок не найдено.", reply_markup=kb.main_kb())


if __name__ == '__main__':
    asyncio.run(dp.start_polling(bot))
