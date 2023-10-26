from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup

import db


def main_kb():
    markup = InlineKeyboardBuilder()
    markup.adjust(*[1] * 3)
    markup.row(InlineKeyboardButton(text="➕ Создать заметку", callback_data="create_note"),
               InlineKeyboardButton(text="📂 Все заметки", callback_data="all_notes"),
               InlineKeyboardButton(text="🔍 Найти заметку", callback_data="find_note"), width=1)
    return markup.as_markup()


def back_kb():
    markup = InlineKeyboardBuilder()
    markup.adjust(1)
    markup.add(InlineKeyboardButton(text="↩ Назад", callback_data="back"))
    return markup.as_markup()


def get_notes(notes, page):
    markup = InlineKeyboardBuilder()
    item = 0
    count_notes = ((page + 1) * 10) - (page * 10)
    for i in range(page * 10, (page + 1) * 10):
        note = notes[i]
        markup.button(text=f"{note[2]}", callback_data=f"note_{note[0]}")
        if not i + 1 == len(notes):
            item += 1
        else:
            if page != 0:
                markup.button(text="⬅", callback_data=f"prev_page:{page}")
            break

        if item == 10 and page != 0:
            markup.add(InlineKeyboardButton(text="⬅", callback_data=f"prev_page:{page}"),
                       InlineKeyboardButton(text="➡", callback_data=f"next_page:{page}"))
            break
        elif item == 10:
            markup.button(text="➡", callback_data=f"next_page:{page}")
            break

    markup.button(text="🏠 В главное меню", callback_data="back")
    markup.adjust(*[1] * count_notes, 2, 1)
    return markup.as_markup()


def open_note():
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text="❌ Удалить заметку", callback_data=f"delete_note"),
               InlineKeyboardButton(text="↩ Назад", callback_data="back"))

    return markup.as_markup()
