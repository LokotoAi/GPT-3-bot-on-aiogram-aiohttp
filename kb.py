from aiogram import types

keyboard = types.InlineKeyboardMarkup()
keyboard.add(types.InlineKeyboardButton(text="Нажми и жди", callback_data="confirm"))