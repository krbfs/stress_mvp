from database import save_poll

def create_sample_polls():
    """Создать примеры опросов в БД"""
    
    # Опрос 1: Стресс на работе
    poll_1 = {
        "poll_id": "poll_1",
        "title": "Стресс на работе",
        "description": "Оцените уровень стресса на работе",
        "image_url": "https://via.placeholder.com/400x300?text=Work+Stress",
        "questions": [
            {
                "text": "Как часто вы чувствуете стресс на работе?",
                "options": ["Никогда", "Редко", "Иногда", "Часто", "Всегда"]
            },
            {
                "text": "Влияет ли работа на ваше здоровье?",
                "options": ["Не влияет", "Слабо влияет", "Умеренно влияет", "Сильно влияет"]
            },
            {
                "text": "Вы считаете рабочую нагрузку?",
                "options": ["Легкой", "Нормальной", "Высокой", "Очень высокой"]
            },
            {
                "text": "Вам хватает времени на отдых?",
                "options": ["Да, полностью", "В основном да", "Иногда", "Нет, никогда"]
            }
        ]
    }
    
    # Опрос 2: Здоровье и образ жизни
    poll_2 = {
        "poll_id": "poll_2",
        "title": "Здоровье и образ жизни",
        "description": "Расскажите о вашем образе жизни",
        "image_url": "https://via.placeholder.com/400x300?text=Health",
        "questions": [
            {
                "text": "Сколько часов вы спите в сутки?",
                "options": ["< 5 часов", "5-6 часов", "7-8 часов", "> 8 часов"]
            },
            {
                "text": "Занимаетесь ли вы спортом?",
                "options": ["Не занимаюсь", "Редко", "2-3 раза в неделю", "Ежедневно"]
            },
            {
                "text": "Как вы оцениваете свое здоровье?",
                "options": ["Плохое", "Среднее", "Хорошее", "Отличное"]
            }
        ]
    }
    
    try:
        save_poll(
            poll_1["poll_id"],
            poll_1["title"],
            poll_1["description"],
            poll_1["questions"],
            poll_1["image_url"]
        )
        print("✅ Опрос 1 создан")
    except Exception as e:
        print(f"⚠️ Опрос 1 уже существует или ошибка: {e}")
    
    try:
        save_poll(
            poll_2["poll_id"],
            poll_2["title"],
            poll_2["description"],
            poll_2["questions"],
            poll_2["image_url"]
        )
        print("✅ Опрос 2 создан")
    except Exception as e:
        print(f"⚠️ Опрос 2 уже существует или ошибка: {e}")

if __name__ == "__main__":
    from database import init_db
    init_db()
    create_sample_polls()