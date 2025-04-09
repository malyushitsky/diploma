from aiogram.fsm.state import StatesGroup, State

class ArticleStates(StatesGroup):
    choosing_action = State()
    entering_url = State()
    asking_question = State()