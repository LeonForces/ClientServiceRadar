from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

import schedule
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

# URL страницы с отзывами
URL = 'https://www.banki.ru/services/responses/bank/promsvyazbank/?type=all'

# Список для хранения ID пользователей
user_ids = set()

# Переменная для хранения времени последнего отзыва
last_review_time = None

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_ids.add(user_id)
    print(f"Добавлен пользователь: {user_id}")  # Отладочный вывод
    await update.message.reply_text("Здравствуйте! Вы подключились к системе оповещения")

# Функция для отправки сообщений всем пользователям
async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if user_ids:
        for user_id in user_ids:
            try:
                await context.bot.send_message(chat_id=user_id, text="Критическое событие")
            except Exception as e:
                print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
    else:
        await update.message.reply_text("Нет зарегистрированных пользователей для отправки.")

def initialize_last_review_time():
    """Инициализация времени последнего отзыва при первом запуске."""
    global last_review_time

    # Делаем GET-запрос к URL
    response = requests.get(URL)

    # Парсим HTML с помощью BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Находим последний элемент с отзывом (предполагается, что последний отзыв находится последним в списке)
    review_time_element = soup.find('span', class_='l0caf3d5f') # предположительный селектор
    if review_time_element:
        review_time_str = review_time_element.text.strip()

        try:
            # Преобразуем строку в объект datetime
            last_review_time = datetime.strptime(review_time_str, '%d.%m.%Y %H:%M')
            print(f'Последнее время отзыва установлено: {last_review_time.strftime("%Y-%m-%d %H:%M:%S")}')
        except ValueError as e:
            print(f'Ошибка при преобразовании строки даты: {e}')
            return None
    else:
        print("Не удалось найти элемент с последним отзывом.")
        return None

def parse_reviews():
    # Функция для получения времени последнего отзыва
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Предположим, что дата и время находятся внутри элемента с классом 'review-time'
    review_time_element = soup.find('span', class_='l0caf3d5f')
    if review_time_element:
        review_time_str = review_time_element.text.strip()

        try:
            # Преобразуем строку в объект datetime
            review_time = datetime.strptime(review_time_str, '%d.%m.%Y %H:%M')

            return review_time
        except ValueError as e:
            print(f'Ошибка при преобразовании строки даты: {e}')
            return None
    else:
        print("Не удалось найти элемент с временем последнего отзыва.")
        return None


def check_for_new_reviews():
    # Получаем текущее время
    global last_review_time

    # Парсим время последнего отзыва
    review_time = parse_reviews()

    if review_time is not None:
        # Проверяем, есть ли новые отзывы за последние 10 минут
        if review_time != last_review_time:

            print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Есть новые отзывы! {review_time}')
            last_review_time = review_time

        else:
            print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Нет новых отзывов. Последний отзыв был {last_review_time}')
    else:
        print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Ошибка при получении времени последнего отзыва.')

# Запуск бота
def main() -> None:
    application = Application.builder().token("8113939811:AAEPFYjLUd0vt4uJx2ytm1LBPrngpBj6N00").build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("send_all", broadcast_message))


    # Планировщик задач
    schedule.every(1).minutes.do(check_for_new_reviews)

    initialize_last_review_time()
    # Запуск планировщика
    while True:
        schedule.run_pending()
        time.sleep(1)

    application.run_polling()


if __name__ == "__main__":
    main()