import requests
import csv
from bs4 import BeautifulSoup

url = 'https://www.banki.ru/services/responses/bank/promsvyazbank/?page=1&is_countable=on'

response = requests.get(url)

# Проверяем статус ответа
links = []
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
                links.append(link)
else:
    print(f'Ошибка при получении данных. Код статуса: {response.status_code}')



with open("parsed_data.csv", mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Rate', 'Header', 'Description'])

    for link in links:
        url_base = 'https://www.banki.ru'
        url = url_base + link
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            rate = soup.find('div', class_=['rating-grade rating-grade--color-1 rating-grade--filled',
                                            'rating-grade rating-grade--color-2 rating-grade--filled',
                                            'rating-grade rating-grade--color-3 rating-grade--filled',
                                            'rating-grade rating-grade--color-4 rating-grade--filled',
                                            'rating-grade rating-grade--color-5 rating-grade--filled', ])
            header = soup.find('h1', class_='text-header-0 le856f50c')
            desc = soup.find('div', class_='lb1789875 markdown-inside markdown-inside--list-type_circle-fill')

            writer.writerow([rate.get_text(strip=True),
                             header.get_text(strip=True),
                             desc.get_text(separator=" ", strip=True).replace("\n", " ").replace("\r", "")])

        else:
            print(f'Ошибка при получении данных. Код статуса: {response.status_code}')
