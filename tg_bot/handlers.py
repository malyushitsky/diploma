from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import ArticleStates
from keyboards import main_menu_keyboard
from api_client import ingest, summarize, ask, summarize_async, ingest_async, ask_async, get_task_result

import asyncio

router = Router()

@router.message(F.text.lower() == "/start")
async def start_handler(msg: Message, state: FSMContext):
    await msg.answer("👋 Привет! Я помогу тебе работать с научными статьями. Для начала нужно загрузить интересуюзщую тебя статью с arXiv.org. Для навигации по боту используй внутреннее меню:", reply_markup=main_menu_keyboard())
    await state.set_state(ArticleStates.choosing_action)

@router.message(F.text.lower() == "⬇️ загрузить статью")
async def ingest_prompt(msg: Message, state: FSMContext):
    await msg.answer("🔗 Отправь ссылку на статью с arXiv:")
    await state.set_state(ArticleStates.entering_url)

@router.message(ArticleStates.entering_url)
async def ingest_article_handler(msg: Message, state: FSMContext):
    user_id = str(msg.from_user.id)
    wait_msg = await msg.answer("📥 Загружаю и обрабатываю статью, подождите немного...")

    task_info = ingest_async(user_id, msg.text)
    task_id = task_info["task_id"]

    # Пуллинг результата
    while True:
        await asyncio.sleep(2)
        status_info = get_task_result(task_id)

        if status_info["status"] == "completed":
            result = status_info["result"]
            await wait_msg.delete()
            await msg.answer(f"✅ {result.get('message')}")
            break
        elif status_info["status"] == "failed":
            await wait_msg.delete()
            await msg.answer(f"❌ Ошибка при загрузке: {status_info['error']}")
            break

    await state.set_state(ArticleStates.choosing_action)


@router.message(F.text.lower() == "📊 суммаризация")
async def summarize_handler(msg: Message, state: FSMContext):
    user_id = str(msg.from_user.id)
    wait_msg = await msg.answer("🧠 Подождите, суммаризация запущена...")

    # Отправляем запрос на запуск задачи через FastAPI
    task_info = summarize_async(user_id)
    task_id = task_info["task_id"]

    # Пуллинг результата
    while True:
        await asyncio.sleep(2)
        status_info = get_task_result(task_id)

        if status_info["status"] == "completed":
            result = status_info["result"]
            await wait_msg.delete()
            await msg.answer(
                f"🌐 <b>{result['title']}</b>\n\n<b>Резюме:</b>\n{result['summary']}",
                parse_mode="HTML"
            )
            break
        elif status_info["status"] == "failed":
            await wait_msg.delete()
            await msg.answer(f"Ошибка: {status_info['error']}")
            break
            
    await state.set_state(ArticleStates.choosing_action)

@router.message(F.text.lower() == "❓ задать вопрос")
async def ask_prompt(msg: Message, state: FSMContext):
    await msg.answer("📝 Напиши вопрос по статье:")
    await state.set_state(ArticleStates.asking_question)


@router.message(ArticleStates.asking_question)
async def ask_handler(msg: Message, state: FSMContext):
    user_id = str(msg.from_user.id)
    wait_msg = await msg.answer("🤖 Думаю над ответом...")

    # Отправляем запрос на запуск задачи через FastAPI
    task_info = ask_async(user_id, msg.text)
    task_id = task_info["task_id"]

    # Пуллинг результата
    while True:
        await asyncio.sleep(2)
        status_info = get_task_result(task_id)

        if status_info["status"] == "completed":
            result = status_info["result"]
            await wait_msg.delete()
            await msg.answer(
                f"💬 <b>Ответ:</b>\n{result['answer']}",
                parse_mode="HTML"
            )
            break
        elif status_info["status"] == "failed":
            await wait_msg.delete()
            await msg.answer(f"Ошибка: {status_info['error']}")
            break

    await state.set_state(ArticleStates.choosing_action)