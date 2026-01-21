import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from handlers import start, button_callback
from database import init_db

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

def main():
    init_db()
    
    app = Application.builder().token(TOKEN).build()
    
    # Команды
    app.add_handler(CommandHandler("start", start))
    
    # Обработка кнопок
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()