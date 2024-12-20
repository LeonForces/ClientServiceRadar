import schedule
import time
from datetime import datetime


last_update_time = datetime.now()


# Задача, которую будем выполнять каждые 10 минут
def scheduled_task():
    global last_update_time

    current_time = datetime.now()

    if not last_update_time or (current_time - last_update_time).total_seconds() < 600:
        last_update_time = current_time
    else:
        print('Прошло больше 10 минут с последнего обновления, пропускаю обработку.')


# Планируем задачу на каждые 10 минут
schedule.every(10).minutes.do(scheduled_task)

# Основной цикл программы
while True:
    schedule.run_pending()
    time.sleep(1)