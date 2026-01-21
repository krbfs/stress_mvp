"""
Пример как добавить логирование кликов в handlers.py
Добавьте эти функции в существующий handlers.py
"""

from telegram import Update
from telegram.ext import ContextTypes
from click_analytics import log_click, format_click_report

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start"""
    user = update.effective_user
    user_id = user.id
    
    # Логируем клик
    log_click(user_id, "start_command")
    
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    keyboard = [
        [InlineKeyboardButton("Начать опрос", callback_data="start_poll")],
        [InlineKeyboardButton("Результаты", callback_data="show_results")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n\n"
        "Это бот для проведения опросов. Выберите действие:",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на кнопки с логированием"""
    query = update.callback_query
    user_id = update.effective_user.id
    
    await query.answer()
    
    # Логируем каждый клик
    log_click(user_id, query.data)
    
    if query.data == "start_poll":
        await start_poll(query, context, user_id)
        log_click(user_id, "view_polls_list")
    
    elif query.data == "show_results":
        await show_results(query, context)
        log_click(user_id, "view_results")
    
    elif query.data.startswith("poll_"):
        poll_id = query.data.replace("poll_", "")
        await show_poll_question(query, context, user_id, poll_id, 0)
        log_click(user_id, f"started_poll_{poll_id}", poll_id=poll_id)
    
    elif query.data.startswith("answer_"):
        parts = query.data.split("_")
        poll_id = parts[1]
        question_idx = int(parts[2])
        answer_idx = int(parts[3])
        
        # Логируем клик по ответу
        log_click(
            user_id, 
            f"answer_q{question_idx}", 
            poll_id=poll_id,
            question_idx=question_idx
        )
        
        await process_answer(query, context, user_id, poll_id, question_idx, answer_idx)

# В admin.py добавьте команду для просмотра аналитики кликов:

async def admin_click_analytics(query, context):
    """Показать аналитику кликов"""
    from click_analytics import format_click_report, get_click_statistics
    
    report = format_click_report()
    
    if len(report) > 4096:
        await query.edit_message_text(report[:4096])
        await query.message.reply_text(report[4096:])
    else:
        await query.edit_message_text(report)

# Добавьте в admin panel меню:

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать админ панель с аналитикой кликов"""
    user_id = update.effective_user.id
    
    from config import ADMIN_IDS
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ У вас нет доступа к админ панели!")
        return
    
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    keyboard = [
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("📋 Отчеты", callback_data="admin_reports")],
        [InlineKeyboardButton("🔘 Аналитика кликов", callback_data="admin_clicks")],  # НОВОЕ
        [InlineKeyboardButton("📝 Управление опросами", callback_data="admin_polls")],
        [InlineKeyboardButton("👥 Пользователи", callback_data="admin_users")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔐 АДМИН ПАНЕЛЬ\n\n"
        "Выберите действие:",
        reply_markup=reply_markup
    )

# Функция для экспорта аналитики в текст

async def export_click_analytics(poll_id: str = None) -> str:
    """Экспортировать аналитику кликов"""
    from click_analytics import (
        get_total_clicks, get_clicks_by_button, 
        get_click_funnel, get_most_clicked_buttons,
        get_average_clicks_per_user
    )
    
    report = "📊 ПОЛНАЯ АНАЛИТИКА КЛИКОВ\n"
    report += "=" * 50 + "\n\n"
    
    total = get_total_clicks(poll_id)
    report += f"Всего кликов: {total}\n"
    report += f"Среднее кликов на пользователя: {get_average_clicks_per_user(poll_id)}\n\n"
    
    report += "🔘 КЛИКИ ПО КНОПКАМ\n"
    buttons = get_clicks_by_button(poll_id)
    for button, count in list(buttons.items())[:10]:
        pct = (count / total * 100) if total > 0 else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        report += f"{button:20} {bar} {pct:5.1f}% ({count})\n"
    
    report += "\n🔀 ВОРОНКА (FUNNEL)\n"
    if poll_id:
        funnel = get_click_funnel(poll_id)
        for step, users in funnel.items():
            report += f"  {step}: {users} пользователей\n"
    
    return report