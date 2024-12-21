import requests
import csv
from bs4 import BeautifulSoup
import time

def get_links():
    url = 'https://www.banki.ru/services/responses/bank/promsvyazbank/?page=10&is_countable=on'

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
                        # links.append(link)
                        print(link)
        else:
            print(f'Ошибка при получении данных. Код статуса: {response.status_code}')
            print(i)
        time.sleep(3)

    with open("links.txt", 'w', encoding='utf-8') as file:
        for link in links:
            file.write(link + '\n')


def get_reviews():
    i = 1
    with open("links.txt", 'r', encoding='utf-8') as read_file:
        with open("parsed_data.csv", mode='w', newline='', encoding='utf-8') as write_file:
            writer = csv.writer(write_file)
            writer.writerow(['Rate', 'Header', 'Description'])
            for line in read_file:
                link = line.strip()
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
                print(i)
                i += 1
                time.sleep(5)

if __name__ == "__main__":
    get_links()
    get_reviews()