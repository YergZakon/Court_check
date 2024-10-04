import streamlit as st
import json
from collections import defaultdict
import os
import anthropic
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем API ключ из переменной окружения
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not ANTHROPIC_API_KEY:
    raise ValueError("API ключ Anthropic не найден. Убедитесь, что он установлен в переменных окружения или в файле .env")

def load_cases(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def get_value(case, key):
    for k in case.keys():
        if k.lower() == key.lower():
            value = case[k]
            if isinstance(value, list):
                return '; '.join(value)
            return value
    return ""

def analyze_cases(cases):
    decisions = defaultdict(list)
    total_cases = len(cases)
    satisfied = 0
    partially_satisfied = 0
    rejected = 0

    for case in cases:
        decision = get_value(case, "итоговое_решение").lower()
        
        if "удовлетворить" in decision and "частично" not in decision:
            satisfied += 1
        elif "частично" in decision and "удовлетворить" in decision:
            partially_satisfied += 1
        elif "отказать" in decision or "оставить без удовлетворения" in decision:
            rejected += 1

        key_factors = {
            "суть_спора": get_value(case, "суть_спора"),
            "требования_истца": get_value(case, "требования_истца"),
            "аргументы_истца": get_value(case, "аргументы_истца"),
            "позиция_ответчика": get_value(case, "позиция_ответчика"),
            "правовая_позиция_суда": get_value(case, "правовая_позиция_суда"),
        }
        decisions[decision].append(key_factors)

    stats = {
        "total_cases": total_cases,
        "satisfied": satisfied,
        "partially_satisfied": partially_satisfied,
        "rejected": rejected
    }

    return decisions, stats

def claude_analysis(decisions, stats):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    prompt = f"""Проанализируй следующие судебные решения и найди отклонения от основной практики:

{json.dumps(decisions, ensure_ascii=False, indent=2)}

Обрати внимание на следующие аспекты:
1. Определи основную практику принятия решений.
2. Найди все случаи, где решение отличается от основной практики.
3. Проанализируй факторы, которые могли повлиять на отклонение от основной практики.
4. Оцени, насколько обоснованы эти отклонения с юридической точки зрения.
5. Предложи возможные объяснения для отклонений.

Представь свой анализ в структурированном виде, выделяя основные выводы и наблюдения."""

    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        # Проверяем тип message.content и извлекаем текст
        if isinstance(message.content, str):
            analysis = message.content
        elif isinstance(message.content, list):
            # Если это список, объединяем тексты из всех элементов
            analysis = ''.join([block.text for block in message.content if hasattr(block, 'text')])
        else:
            # Если это другой тип, пытаемся привести к строке
            analysis = str(message.content)
        return analysis.strip()
    except Exception as e:
        return f"Ошибка при анализе: {str(e)}"
        
def save_analysis_to_file(analysis, stats, output_file):
    combined_data = {
        "statistics": stats,
        "analysis": analysis
    }
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(combined_data, file, ensure_ascii=False, indent=2)
    st.success(f"Анализ сохранен в файл: {output_file}")

def parse_analysis(analysis):
    return analysis

def main():
    st.title("Анализ судебных решений")

    categories = [
        "О_банкротстве_в_т.ч_юридического_лица",
        "о_направлении_гражданина__больного_алкоголизмом__etc",
        "О_признании_сделки_недействительной",
        "ОБ_ОБЯЗАНИИ__ПОНУЖДЕНИИ_(ИСПОЛНЕНИЯ_ТРЕБОВАНИЯ_etc",
        "Об_установлении_фактов__имеющих_юридическое_значение",
        "Об_установлении_фактов__имеющих_юридическое_значение_etc",
        "По_жалобам_на_нотариальные_действия_или_отказ_etc",
    ]    

    selected_category = st.selectbox("Выберите категорию дела", categories)

    if st.button("Провести анализ"):
        input_file = f"{selected_category}.json"
        output_file = f"{selected_category}_analysis.json"

        try:
            cases = load_cases(input_file)
            decisions, stats = analyze_cases(cases)
            analysis = claude_analysis(decisions, stats)

            if analysis.startswith("Ошибка при анализе"):
                st.error(analysis)
            else:
                save_analysis_to_file(analysis, stats, output_file)

                st.subheader("Статистика по делам:")
                st.write(f"Всего дел: {stats['total_cases']}")
                st.write(f"Удовлетворено исков: {stats['satisfied']}")
                st.write(f"Частично удовлетворено: {stats['partially_satisfied']}")
                st.write(f"Отказано: {stats['rejected']}")

                st.subheader("Результаты анализа:")
                parsed_analysis = parse_analysis(analysis)
                st.markdown(parsed_analysis)

        except Exception as e:
            st.error(f"Произошла ошибка при анализе: {str(e)}")

if __name__ == "__main__":
    main()
