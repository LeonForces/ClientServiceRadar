import schedule
import time
from datetime import datetime

# Импортируем библиотеки для работы с веб-запросами и парсингом HTML
import requests
from bs4 import BeautifulSoup

# Указываем URL страницы с отзывами
URL = 'https://www.banki.ru/services/responses/bank/promsvyazbank/?type=all'


def parse_reviews():
    # Функция для получения времени последнего отзыва
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Предположим, что дата и время находятся внутри элемента с классом 'review-time'
    last_review_time_element = soup.find('div', class_='lb3db10af l594410f5 l7c75331c')
    if last_review_time_element:
        last_review_time_str = last_review_time_element.text.strip()

        try:
            # Преобразуем строку в объект datetime
            last_review_time = datetime.strptime(last_review_time_str, '%Y-%m-%d %H:%M:%S')

            return last_review_time
        except ValueError as e:
            print(f'Ошибка при преобразовании строки даты: {e}')
            return None
    else:
        print("Не удалось найти элемент с временем последнего отзыва.")
        return None


def check_for_new_reviews():
    # Получаем текущее время
    current_time = datetime.now()

    # Парсим время последнего отзыва
    last_review_time = parse_reviews()

    print(last_review_time)

    # if last_review_time is not None:
    #     # Проверяем, есть ли новые отзывы за последние 10 минут
    #     if (current_time - last_review_time).total_seconds() <= 600:
    #         print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Есть новые отзывы!')
    #     else:
    #         print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Нет новых отзывов.')
    # else:
    #     print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: Ошибка при получении времени последнего отзыва.')


# Планируем выполнение задачи каждую минуту для тестирования
schedule.every(10).minutes.do(check_for_new_reviews)

while True:
    schedule.run_pending()
    time.sleep(1)