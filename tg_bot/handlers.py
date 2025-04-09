from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import ArticleStates
from keyboards import main_menu_keyboard
from api_client import ingest_article, summarize, ask
import asyncio

router = Router()

@router.message(F.text.lower() == "/start")
async def start_handler(msg: Message, state: FSMContext):
    await msg.answer("👋 Привет! Я помогу тебе работать с научными статьями. Выбери действие:", reply_markup=main_menu_keyboard())
    await state.set_state(ArticleStates.choosing_action)

@router.message(F.text.lower() == "⬇️ загрузить статью")
async def ingest_prompt(msg: Message, state: FSMContext):
    await msg.answer("🔗 Отправь ссылку на статью с arXiv:")
    await state.set_state(ArticleStates.entering_url)

@router.message(ArticleStates.entering_url)
async def ingest_article_handler(msg: Message, state: FSMContext):
    user_id = str(msg.from_user.id)
    wait_msg = await msg.answer("📥 Загружаю и обрабатываю статью, подождите немного...")
    result = ingest_article(user_id, msg.text)
    await wait_msg.delete()
    await msg.answer(f"✅ {result.get('message')}")
    await state.set_state(ArticleStates.choosing_action)


@router.message(F.text.lower() == "📊 суммаризация")
async def summarize_handler(msg: Message, state: FSMContext):
    user_id = str(msg.from_user.id)
    wait_msg = await msg.answer("🧠 Подождите немного, я готовлю краткое резюме статьи...")
    result = summarize(user_id)
    await wait_msg.delete()
    if "error" in result:
        await msg.answer(result["error"])
    else:
        await msg.answer(
            f"🌐 <b>{result['title']}</b>\n\n<b>Резюме:</b>\n{result['summary']}",
            parse_mode="HTML"
        )
    await state.set_state(ArticleStates.choosing_action)


@router.message(F.text.lower() == "❓ задать вопрос")
async def ask_prompt(msg: Message, state: FSMContext):
    await msg.answer("📝 Напиши вопрос по статье:")
    await state.set_state(ArticleStates.asking_question)

@router.message(ArticleStates.asking_question)
async def ask_handler(msg: Message, state: FSMContext):
    user_id = str(msg.from_user.id)
    wait_msg = await msg.answer("🤖 Думаю над ответом...")
    result = ask(user_id, msg.text)
    await wait_msg.delete()
    if "error" in result:
        await msg.answer(result["error"])
    else:
        await msg.answer(f"💬 <b>Ответ:</b>\n{result['answer']}", parse_mode="HTML")
    await state.set_state(ArticleStates.choosing_action)