"""
Логирование для отладки и мониторинга
"""
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def log_user_action(user_id, action, details=None):
    """Логировать действие пользователя"""
    msg = f"User {user_id} - {action}"
    if details:
        msg += f" - {details}"
    logger.info(msg)

def log_poll_started(user_id, poll_id):
    """Логировать начало опроса"""
    log_user_action(user_id, "started_poll", f"poll_id={poll_id}")

def log_poll_completed(user_id, poll_id, answers_count):
    """Логировать завершение опроса"""
    log_user_action(user_id, "completed_poll", f"poll_id={poll_id}, answers={answers_count}")

def log_error(error_type, error_msg, user_id=None):
    """Логировать ошибку"""
    msg = f"ERROR: {error_type} - {error_msg}"
    if user_id:
        msg += f" (user_id={user_id})"
    logger.error(msg)

def log_admin_action(admin_id, action, details=None):
    """Логировать админ действие"""
    msg = f"ADMIN {admin_id} - {action}"
    if details:
        msg += f" - {details}"
    logger.warning(msg)