import os
import json
import random
import threading
from flask import Flask
import telebot
from telebot import types

# -------------------------------------------------------------------------
# 1. FLASK-СЕРВЕР ДЛЯ ПИНГА (KEEP-ALIVE)
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
# 3. ДИНАМИЧЕСКИЙ БАНК ЗАДАЧ ИЗ JSON
# -------------------------------------------------------------------------
class FIPIBank:
    """Загрузчик задач из JSON-файлов в папке data/."""

    SUBJECTS = {
        "math": {"name": "📐 Математика"},
        "rus":  {"name": "📚 Русский язык"},
        "phys": {"name": "⚡ Физика"},
        "cs":   {"name": "💻 Информатика"}
    }

    @staticmethod
    def load_all_tasks(subject_code):
        """Загружает список задач из файла data/{subject_code}.json"""
        filepath = f"data/{subject_code}.json"
        if not os.path.exists(filepath):
            return []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Ошибка чтения файла {filepath}: {e}")
            return []

    @staticmethod
    def get_task(subject_code, task_num=None):
        """Возвращает случайную задачу по номеру или из всего предмета."""
        all_tasks = FIPIBank.load_all_tasks(subject_code)
        if not all_tasks:
            return None

        if task_num is not None:
            filtered = [t for t in all_tasks if str(t.get("num")) == str(task_num)]
            if not filtered:
                return None
            task = random.choice(filtered).copy()
        else:
            task = random.choice(all_tasks).copy()

        task["subject"] = subject_code
        return task

    @staticmethod
    def get_available_numbers(subject_code):
        """Возвращает список доступных номеров заданий для предмета."""
        tasks = FIPIBank.load_all_tasks(subject_code)
        numbers = sorted(list(set(int(t["num"]) for t in tasks if "num" in t)))
        return numbers

    @staticmethod
    def get_full_variant(subject_code):
        """Формирует вариант: по 1 случайной задаче каждого доступного номера."""
        tasks = FIPIBank.load_all_tasks(subject_code)
        if not tasks:
            return []

        numbers = sorted(list(set(int(t["num"]) for t in tasks if "num" in t)))
        variant = []
        for num in numbers:
            t = FIPIBank.get_task(subject_code, task_num=num)
            if t:
                variant.append(t)
        return variant

# -------------------------------------------------------------------------
# 4. ВСПАМОГАТЕЛЬНЫЕ ФУНКЦИИ ОТПРАВКИ
# -------------------------------------------------------------------------
def send_task_message(user_id, task, prefix_text=""):
    """Отправляет задачу с фото (если есть) или текстом."""
    caption = (
        f"{prefix_text}"
        f"📌 **Задание №{task['num']}** ({task.get('topic', 'Тема не указана')})\n\n"
        f"❓ {task['question']}\n\n"
        f"👉 *Отправь ответ сообщением в чат:*"
    )

    photo_id = task.get("photo", "").strip()
    if photo_id:
        bot.send_photo(user_id, photo=photo_id, caption=caption, parse_mode="Markdown")
    else:
        bot.send_message(user_id, caption, parse_mode="Markdown")

def send_next_variant_task(user_id):
    queue = user_data[user_id]["variant_queue"]
    if queue:
        task = queue.pop(0)
        user_data[user_id]["current_task"] = task
        prefix = f"📝 **Вариант ЕГЭ** (Осталось задач: {len(queue) + 1})\n\n"
        send_task_message(user_id, task, prefix_text=prefix)
    else:
        user_data[user_id]["mode"] = None
        user_data[user_id]["current_task"] = None
        bot.send_message(user_id, "🎉 **Поздравляем! Ты полностью прошёл вариант ЕГЭ.**", reply_markup=get_main_menu())

# -------------------------------------------------------------------------
# 5. КЛАВИАТУРЫ И МЕНЮ
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
# 6. ОБРАБОТЧИКИ СООБЩЕНИЙ И CALLBACKS
# -------------------------------------------------------------------------
@bot.message_handler(commands=['start'])
def cmd_start(message):
    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        f"Это бот-тренажёр **ЕГЭ из банка ФИПИ**.\n"
        f"Выбирай предмет и начинай подготовку!",
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
        available_nums = FIPIBank.get_available_numbers(sub_code)

        if not available_nums:
            bot.answer_callback_query(call.id, "В базе пока нет задач по этому предмету!", show_alert=True)
            return

        markup = types.InlineKeyboardMarkup(row_width=3)
        buttons = [types.InlineKeyboardButton(f"№{num}", callback_data=f"gen_{sub_code}_{num}") for num in available_nums]
        markup.add(*buttons)
        markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data=f"sub_{sub_code}"))

        bot.edit_message_text("Выбери номер задания для нарезки:", chat_id=user_id, message_id=call.message.message_id, reply_markup=markup)

    elif data.startswith("gen_"):
        _, sub_code, num = data.split("_")
        task = FIPIBank.get_task(sub_code, task_num=num)

        if not task:
            bot.send_message(user_id, "Не удалось найти задачу с этим номером.")
            return

        user_data[user_id]["mode"] = "single"
        user_data[user_id]["current_task"] = task
        send_task_message(user_id, task)

    elif data.startswith("act_variant_"):
        sub_code = data.split("_")[2]
        variant_queue = FIPIBank.get_full_variant(sub_code)

        if not variant_queue:
            bot.answer_callback_query(call.id, "Недостаточно задач для формирования варианта!", show_alert=True)
            return

        user_data[user_id]["mode"] = "variant"
        user_data[user_id]["variant_queue"] = variant_queue

        bot.send_message(user_id, f"🚀 **Вариант сформирован!** Всего заданий: {len(variant_queue)}.\nНачинаем прорешивание.")
        send_next_variant_task(user_id)

@bot.message_handler(func=lambda msg: True)
def check_user_answer(message):
    user_id = message.chat.id
    if user_id not in user_data or user_data[user_id]["current_task"] is None:
        bot.send_message(user_id, "Выбери предмет и задание в меню ниже 👇", reply_markup=get_main_menu())
        return

    task = user_data[user_id]["current_task"]
    user_ans = message.text.strip().lower()
    correct_ans = str(task["answer"]).strip().lower()

    user_data[user_id]["total"] += 1

    sub_code = task["subject"]
    task_num = task["num"]
    next_markup = types.InlineKeyboardMarkup()
    next_markup.add(types.InlineKeyboardButton(f"🔄 Следующее Задание №{task_num}", callback_data=f"gen_{sub_code}_{task_num}"))

    solution_text = task.get('solution', 'Разбор отсутствует.')

    if user_ans == correct_ans:
        user_data[user_id]["correct"] += 1
        bot.send_message(
            user_id,
            f"✅ **Верно!**\n\n💡 **Разбор решения:**\n{solution_text}",
            parse_mode="Markdown"
        )
    else:
        bot.send_message(
            user_id,
            f"❌ **Неверно.**\n"
            f"Правильный ответ: `{task['answer']}`\n\n"
            f"💡 **Разбор решения:**\n{solution_text}",
            parse_mode="Markdown"
        )

    if user_data[user_id]["mode"] == "single":
        bot.send_message(user_id, "Хочешь закрепить материал?", reply_markup=next_markup)
        user_data[user_id]["current_task"] = None
    elif user_data[user_id]["mode"] == "variant":
        send_next_variant_task(user_id)

# -------------------------------------------------------------------------
# 7. ЗАПУСК FLASK + TELEGRAM BOT
# -------------------------------------------------------------------------
if __name__ == "__main__":
    t = threading.Thread(target=run_http)
    t.start()

    print("Бот запущен на базе JSON-хранилища...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
