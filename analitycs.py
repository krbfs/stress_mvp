from database import get_poll
from collections import defaultdict

def analyze_responses(poll_id, responses):
    """Анализировать ответы на опрос"""
    poll = get_poll(poll_id)
    
    if not poll:
        return {}
    
    analysis = {}
    questions = poll["questions"]
    
    for q_idx, question in enumerate(questions):
        question_key = f"q_{q_idx}"
        answer_counts = defaultdict(int)
        
        # Подсчитываем количество каждого ответа
        for response in responses:
            user_answer = response["answers"].get(question_key)
            if user_answer:
                answer_counts[user_answer] += 1
        
        analysis[q_idx] = {
            "question_text": question["text"],
            "answer_counts": dict(answer_counts),
            "total_answered": sum(answer_counts.values())
        }
    
    return analysis

def calculate_stress_level(answers):
    """Пример: вычислить уровень стресса на основе ответов"""
    stress_scores = {
        "Никогда": 0,
        "Редко": 1,
        "Иногда": 2,
        "Часто": 3,
        "Всегда": 4
    }
    
    total_score = 0
    count = 0
    
    for key, answer in answers.items():
        if answer in stress_scores:
            total_score += stress_scores[answer]
            count += 1
    
    if count == 0:
        return 0
    
    average_score = total_score / count
    
    if average_score < 1:
        return "Низкий уровень стресса 😊"
    elif average_score < 2:
        return "Умеренный уровень стресса 😐"
    elif average_score < 3:
        return "Выше среднего уровень стресса 😟"
    else:
        return "Высокий уровень стресса 😰"

def generate_report(poll_id, responses):
    """Генерировать подробный отчет по результатам"""
    analysis = analyze_responses(poll_id, responses)
    
    report = "📋 ПОДРОБНЫЙ ОТЧЕТ\n"
    report += "=" * 40 + "\n\n"
    
    for q_idx, data in analysis.items():
        report += f"Вопрос {q_idx + 1}: {data['question_text']}\n"
        report += f"Всего ответов: {data['total_answered']}\n"
        
        for answer, count in sorted(data['answer_counts'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / data['total_answered'] * 100) if data['total_answered'] > 0 else 0
            bar_length = int(percentage / 5)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            report += f"{answer:20} {bar} {percentage:5.1f}% ({count})\n"
        
        report += "\n"
    
    return report