import schedule
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

# Указываем URL страницы с отзывами
URL = 'https://www.banki.ru/services/responses/bank/promsvyazbank/?type=all'

# Переменная для хранения времени последнего отзыва
last_review_time = None


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


# Планируем выполнение задачи каждую минуту для тестирования
schedule.every(1).minutes.do(check_for_new_reviews)

if __name__ == "__main__":
    initialize_last_review_time()
    while True:
        schedule.run_pending()
        time.sleep(1)