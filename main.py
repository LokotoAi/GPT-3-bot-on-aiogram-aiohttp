import config
import kb
import hashlib
import logging
import aiohttp
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent, InlineQuery

logging.basicConfig(level=logging.DEBUG)
bot = Bot(token=config.api_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class Form(StatesGroup):
    gpt3 = State()

@dp.message_handler()
async def generate(message: types.Message, state: FSMContext):
    text = message.text
    data = {
        "text": text,
    }

    async with aiohttp.ClientSession() as session:
        async with  session.post(config.sURL, headers=config.headers, json=data) as response:
            some = await response.json()
            answer = (some['predictions'])

    async with state.proxy() as data:
        data['gpt3'] = answer

    await bot.send_message(message.chat.id, answer)

@dp.inline_handler()
async def inline_messg(inline_query: InlineQuery, state: FSMContext):
    async with state.proxy() as data:
        data['gpt3'] = inline_query.query

    text = "Пиши сообщение" if not inline_query.query else inline_query.query
    input_content = InputTextMessageContent(text)
    result_id: str = hashlib.md5(text.encode()).hexdigest()
    item = InlineQueryResultArticle(
        id=result_id,
        title=text,
        input_message_content=input_content, reply_markup=kb.keyboard,
    )
    await bot.answer_inline_query(inline_query.id, results=[item], cache_time=60)

    async with state.proxy() as data:
        data['gpt3'] = inline_query.query

@dp.callback_query_handler(lambda c: c.data == 'confirm')
async def inline_answer(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        text = data['gpt3']
    data = {
        "text": text,
    }
    async with aiohttp.ClientSession() as session:
        async with  session.post(config.sURL, headers=config.headers, json=data) as response:
            some = await response.json()
            answer = (some['predictions'])

    await bot.edit_message_text(inline_message_id=callback_query.inline_message_id, text=answer)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)