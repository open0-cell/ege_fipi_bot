import os
import random
import math
import threading
from flask import Flask
import telebot
from telebot import types

# -------------------------------------------------------------------------
# 1. FLASK-СЕРВЕР ДЛЯ ПИНГА (КЕЕP-ALIVE)
# -------------------------------------------------------------------------
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_http():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# -------------------------------------------------------------------------
# 2. ИНИЦИАЛИЗАЦИЯ БОТА И ХРАНИЛИЩА
# -------------------------------------------------------------------------
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

user_data = {}

# -------------------------------------------------------------------------
# 3. БАНК ЗАДАНИЙ ФИПИ
# -------------------------------------------------------------------------
class FIPIBank:
    """Генератор задач ФИПИ по предметам."""

    # --- МАТЕМАТИКА ---
    @staticmethod
    def math_task_1():
        price = random.randint(100, 500) * 10
        discount = random.choice([10, 15, 20, 25, 30, 40, 50])
        ans = price * (100 - discount) // 100
        return {
            "subject": "math", "num": 1, "topic": "Простейшие текстовые задачи",
            "question": f"Товар стоит {price} руб. Во время распродажи скидка составила {discount}%. Сколько стоит товар со скидкой?",
            "answer": str(ans),
            "solution": f"1) Находим стоимость с учетом скидки:\n{price} * (100 - {discount}) / 100 = {ans} руб."
        }

    @staticmethod
    def math_task_2():
        blue = random.randint(3, 12)
        red = random.randint(3, 12)
        green = random.randint(2, 8)
        total = blue + red + green
        ans = round(red / total, 2)
        return {
            "subject": "math", "num": 2, "topic": "Теория вероятностей",
            "question": f"В таксопарке {total} машин: {blue} черных, {red} желтых и {green} зеленых. Найдите вероятность того, что на вызов приедет желтое такси. (Ответ округлите до сотых).",
            "answer": str(ans),
            "solution": f"P = (благоприятные исходы) / (всего) = {red} / {total} ≈ {ans}"
        }

    @staticmethod
    def math_task_3():
        a = random.randint(2, 9)
        b = random.randint(1, 20)
        x = random.randint(-10, 10)
        c = a * x + b
        return {
            "subject": "math", "num": 3, "topic": "Уравнения",
            "question": f"Найдите корень уравнения: {a}x + {b} = {c}",
            "answer": str(x),
            "solution": f"{a}x = {c} - {b}  =>  {a}x = {c - b}  =>  x = {x}"
        }

    # --- РУССКИЙ ЯЗЫК ---
    @staticmethod
    def rus_task_4():
        words = [
            ("звонит", "звонИт", "ударение падает на гласную И"),
            ("торты", "тОрты", "ударение падает на гласную О (неподвижное)"),
            ("красивее", "красИвее", "ударение сохраняется на И"),
            ("квартал", "квартАл", "в любых значениях ударение на А"),
            ("договор", "договОр", "ударение всегда на О")
        ]
        word, correct_stress, rule = random.choice(words)
        return {
            "subject": "rus", "num": 4, "topic": "Орфоэпические нормы (Ударения)",
            "question": f"Укажите правильный вариант произношения слова (напишите слово с заглавной гласной под ударением, например: звонИт):\nСлово: {word}",
            "answer": correct_stress.lower(),
            "solution": f"Верное ударение: **{correct_stress}**.\nПравило: {rule}."
        }

    @staticmethod
    def rus_task_5():
        paronyms = [
            ("Абонент временно недоступен", "абонент", "Абонент — лицо или организация, пользующаяся абонементом."),
            ("Дипломатичный подход к решению проблемы", "дипломатичный", "Дипломатичный — тонкий, умелый, тактичный."),
            ("Искусственный лед на арене", "искусственный", "Искусственный — сделанный подобием настоящего.")
        ]
        text, ans, rule = random.choice(paronyms)
        return {
            "subject": "rus", "num": 5, "topic": "Паронимы",
            "question": f"Впишите выделенное слово в правильной форме:\n«{text}»",
            "answer": ans.lower(),
            "solution": f"Правильно: **{ans}**.\nРазбор: {rule}"
        }

    # --- ФИЗИКА ---
    @staticmethod
    def phys_task_1():
        v = random.randint(10, 30)
        t = random.randint(2, 10)
        s = v * t
        return {
            "subject": "phys", "num": 1, "topic": "Механика (Равномерное движение)",
            "question": f"Тело движется прямолинейно и равномерно со скоростью {v} м/с. Какой путь оно пройдет за {t} секунд?",
            "answer": str(s),
            "solution": f"Формула пути: S = v * t = {v} м/с * {t} с = {s} м."
        }

    @staticmethod
    def phys_task_2():
        m = random.randint(2, 10)
        a = random.randint(2, 6)
        f = m * a
        return {
            "subject": "phys", "num": 2, "topic": "Второй закон Ньютона",
            "question": f"На тело массой {m} кг действует сила, сообщая ему ускорение {a} м/с². Найдите величину этой силы (в Н).",
            "answer": str(f),
            "solution": f"По II закону Ньютона: F = m * a = {m} * {a} = {f} Н."
        }

    # --- ИНФОРМАТИКА ---
    @staticmethod
    def cs_task_1():
        num = random.randint(15, 255)
        ans = bin(num)[2:]
        return {
            "subject": "cs", "num": 1, "topic": "Системы счисления",
            "question": f"Переведите число {num} из десятичной системы счисления в двоичную.",
            "answer": str(ans),
            "solution": f"Последовательно делим {num} на 2 и записываем остатки снизу вверх: {ans}"
        }

    @staticmethod
    def cs_task_2():
        n = random.randint(3, 6)
        ans = math.factorial(n)
        return {
            "subject": "cs", "num": 2, "topic": "Комбинаторика",
            "question": f"Сколькими способами {n} разных файлов можно разместить в каталоге?",
            "answer": str(ans),
            "solution": f"Число перестановок P = {n}! = {ans}"
        }

    SUBJECTS = {
        "math": {"name": "📐 Математика", "tasks": {1: math_task_1, 2: math_task_2, 3: math_task_3}},
        "rus":  {"name": "📚 Русский язык", "tasks": {4: rus_task_4, 5: rus_task_5}},
        "phys": {"name": "⚡ Физика", "tasks": {1: phys_task_1, 2: phys_task_2}},
        "cs":   {"name": "💻 Информатика", "tasks": {1: cs_task_1, 2: cs_task_2}}
    }

# -------------------------------------------------------------------------
# 4. КЛАВИАТУРЫ И МЕНЮ
# -------------------------------------------------------------------------
def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📚 Выбрать предмет"), types.KeyboardButton("📊 Моя статистика"))
    return markup

def get_subject_inline_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    for code, info in FIPIBank.SUBJECTS.items():
        markup.add(types.InlineKeyboardButton(info["name"], callback_data=f"sub_{code}"))
    return markup

def get_action_inline_keyboard(sub_code):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🎯 Выбрать конкретное задание", callback_data=f"act_tasks_{sub_code}"),
        types.InlineKeyboardButton("📝 Начать целый вариант ЕГЭ", callback_data=f"act_variant_{sub_code}"),
        types.InlineKeyboardButton("🔙 Назад к предметам", callback_data="back_to_subjects")
    )
    return markup

# -------------------------------------------------------------------------
# 5. ОБРАБОТЧИКИ СООБЩЕНИЙ И CALLBACKS
# -------------------------------------------------------------------------
@bot.message_handler(commands=['start'])
def cmd_start(message):
    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        f"Это бот-тренажёр **ЕГЭ из банка ФИПИ**.\n"
        f"Здесь ты можешь нарезать отдельные задания или решать целые варианты с подробными разборами!",
        parse_mode="Markdown",
        reply_markup=get_main_menu()
    )

@bot.message_handler(func=lambda msg: msg.text in ["📚 Выбрать предмет", "📊 Моя статистика"])
def handle_text_menu(message):
    user_id = message.chat.id
    if user_id not in user_data:
        user_data[user_id] = {"correct": 0, "total": 0, "mode": None, "variant_queue": [], "current_task": None}

    if message.text == "📚 Выбрать предмет":
        bot.send_message(user_id, "Выбери предмет для подготовки:", reply_markup=get_subject_inline_keyboard())
    elif message.text == "📊 Моя статистика":
        c = user_data[user_id]["correct"]
        t = user_data[user_id]["total"]
        percent = round((c / t * 100), 1) if t > 0 else 0
        bot.send_message(user_id, f"📈 **Твоя статистика:**\n\nРешено задач: {t}\nПравильно: {c}\nТочность: {percent}%", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.message.chat.id
    if user_id not in user_data:
        user_data[user_id] = {"correct": 0, "total": 0, "mode": None, "variant_queue": [], "current_task": None}

    data = call.data

    if data == "back_to_subjects":
        bot.edit_message_text("Выбери предмет для подготовки:", chat_id=user_id, message_id=call.message.message_id, reply_markup=get_subject_inline_keyboard())

    elif data.startswith("sub_"):
        sub_code = data.split("_")[1]
        sub_name = FIPIBank.SUBJECTS[sub_code]["name"]
        bot.edit_message_text(f"Предмет: **{sub_name}**\nЧто будем делать?", chat_id=user_id, message_id=call.message.message_id, parse_mode="Markdown", reply_markup=get_action_inline_keyboard(sub_code))

    elif data.startswith("act_tasks_"):
        sub_code = data.split("_")[2]
        tasks = FIPIBank.SUBJECTS[sub_code]["tasks"]
        markup = types.InlineKeyboardMarkup(row_width=2)
        for num in tasks.keys():
            markup.add(types.InlineKeyboardButton(f"Задание №{num}", callback_data=f"gen_{sub_code}_{num}"))
        markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data=f"sub_{sub_code}"))
        bot.edit_message_text("Выбери номер задания для нарезки:", chat_id=user_id, message_id=call.message.message_id, reply_markup=markup)

    elif data.startswith("gen_"):
        _, sub_code, num = data.split("_")
        task_fn = FIPIBank.SUBJECTS[sub_code]["tasks"][int(num)]
        task = task_fn()
        user_data[user_id]["mode"] = "single"
        user_data[user_id]["current_task"] = task
        
        bot.send_message(
            user_id,
            f"📌 **Задание №{task['num']}** ({task['topic']})\n\n"
            f"❓ {task['question']}\n\n"
            f"👉 *Отправь ответ сообщением в чат:*",
            parse_mode="Markdown"
        )

    elif data.startswith("act_variant_"):
        sub_code = data.split("_")[2]
        tasks_dict = FIPIBank.SUBJECTS[sub_code]["tasks"]
        variant_queue = [fn() for fn in tasks_dict.values()]
        
        user_data[user_id]["mode"] = "variant"
        user_data[user_id]["variant_queue"] = variant_queue
        
        bot.send_message(user_id, f"🚀 **Вариант сформирован!** Всего заданий: {len(variant_queue)}.\nНачинаем прорешивание.")
        send_next_variant_task(user_id)

def send_next_variant_task(user_id):
    queue = user_data[user_id]["variant_queue"]
    if queue:
        task = queue.pop(0)
        user_data[user_id]["current_task"] = task
        bot.send_message(
            user_id,
            f"📝 **Вариант ЕГЭ** (Осталось задач: {len(queue) + 1})\n\n"
            f"📌 **Задание №{task['num']}** ({task['topic']})\n"
            f"❓ {task['question']}\n\n"
            f"👉 *Введи ответ:*",
            parse_mode="Markdown"
        )
    else:
        user_data[user_id]["mode"] = None
        user_data[user_id]["current_task"] = None
        bot.send_message(user_id, "🎉 **Поздравляем! Ты полностью прошел вариант ЕГЭ.**", reply_markup=get_main_menu())

@bot.message_handler(func=lambda msg: True)
def check_user_answer(message):
    user_id = message.chat.id
    if user_id not in user_data or user_data[user_id]["current_task"] is None:
        bot.send_message(user_id, "Выбери предмет и задание в меню ниже 👇", reply_markup=get_main_menu())
        return

    task = user_data[user_id]["current_task"]
    user_ans = message.text.strip().lower()
    correct_ans = task["answer"].strip().lower()

    user_data[user_id]["total"] += 1

    sub_code = task["subject"]
    task_num = task["num"]
    next_markup = types.InlineKeyboardMarkup()
    next_markup.add(types.InlineKeyboardButton(f"🔄 Следующее Задание №{task_num}", callback_data=f"gen_{sub_code}_{task_num}"))

    if user_ans == correct_ans:
        user_data[user_id]["correct"] += 1
        bot.send_message(
            user_id,
            f"✅ **Верно!**\n\n💡 **Разбор решения:**\n{task['solution']}",
            parse_mode="Markdown"
        )
    else:
        bot.send_message(
            user_id,
            f"❌ **Неверно.**\n"
            f"Правильный ответ: `{task['answer']}`\n\n"
            f"💡 **Разбор решения:**\n{task['solution']}",
            parse_mode="Markdown"
        )

    if user_data[user_id]["mode"] == "single":
        bot.send_message(user_id, "Хочешь закрепить материал?", reply_markup=next_markup)
        user_data[user_id]["current_task"] = None
    elif user_data[user_id]["mode"] == "variant":
        send_next_variant_task(user_id)

# -------------------------------------------------------------------------
# 6. ЗАПУСК ДВУХ ПОТОКОВ (FLASK + TELEGRAM BOT)
# -------------------------------------------------------------------------
if __name__ == "__main__":
    t = threading.Thread(target=run_http)
    t.start()
    
    print("Бот запущен...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
