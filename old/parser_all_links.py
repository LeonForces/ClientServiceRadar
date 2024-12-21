import requests
import csv
from bs4 import BeautifulSoup
import time


url = 'https://www.banki.ru/services/responses/bank/promsvyazbank/?page=10&is_countable=on'

response = requests.get(url)

# Начальная страница
current_page = 1

# Проверяем статус ответа
links = []
for i in range(200):
    # Проверенные
    # url = f'https://www.banki.ru/services/responses/bank/promsvyazbank/?page={i}&is_countable=on'
    # Непроверенные
    url = f'https://www.banki.ru/services/responses/bank/promsvyazbank/?page={i}&type=all'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        headers = soup.find_all('div', class_="lf4cbd87d l9656ec89 lb47af913 lced4cbee")
        elements = headers

        # Проходим по каждому элементу и извлекаем ссылку
        for element in elements:
            h3_element = element.find('h3', class_='ldecc766d')
            if h3_element:
                link_element = h3_element.find('a')
                if link_element:
                    link = link_element['href']
                    #links.append(link)
                    print (link)
    else:
        print(f'Ошибка при получении данных. Код статуса: {response.status_code}')
        print(i)
    time.sleep(3)

with open("../links.txt", 'w', encoding='utf-8') as file:
    for link in links:
        file.write(link + '\n')