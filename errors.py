"""
Обработка ошибок и исключений
"""
from telegram import Update
from telegram.ext import ContextTypes
from logger import logger, log_error

class BotException(Exception):
    """Базовое исключение бота"""
    pass

class PollNotFoundError(BotException):
    """Опрос не найден"""
    pass

class UserAlreadyRespondedError(BotException):
    """Пользователь уже ответил на опрос"""
    pass

class DatabaseError(BotException):
    """Ошибка БД"""
    pass

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Update {update} caused error {context.error}")
    
    try:
        if update and update.effective_user:
            user_id = update.effective_user.id
            log_error("UnhandledError", str(context.error), user_id)
            
            # Отправляем сообщение об ошибке пользователю
            if update.message:
                await update.message.reply_text(
                    "❌ Произошла ошибка. Пожалуйста, попробуйте позже или обратитесь к администратору."
                )
            elif update.callback_query:
                await update.callback_query.answer(
                    "❌ Ошибка при обработке запроса",
                    show_alert=True
                )
    except Exception as e:
        logger.error(f"Error in error handler: {e}")

async def validate_poll_exists(poll_id):
    """Проверка существования опроса"""
    from database import get_poll
    
    poll = get_poll(poll_id)
    if not poll:
        raise PollNotFoundError(f"Poll {poll_id} not found")
    return poll

async def validate_user_not_responded(user_id, poll_id):
    """Проверка что пользователь не ответил"""
    from database import user_already_responded
    
    if user_already_responded(user_id, poll_id):
        raise UserAlreadyRespondedError(f"User {user_id} already responded to {poll_id}")

def safe_json_load(data):
    """Безопасная загрузка JSON"""
    import json
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        raise DatabaseError(f"Invalid JSON data: {e}")

def safe_json_dump(data):
    """Безопасное сохранение JSON"""
    import json
    try:
        return json.dumps(data, ensure_ascii=False)
    except Exception as e:
        logger.error(f"JSON encode error: {e}")
        raise DatabaseError(f"Cannot serialize data: {e}")