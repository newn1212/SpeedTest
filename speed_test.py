"""Консольный скрипт для замера скорости скачивания по заданному адресу.

Делает 10 последовательных запросов, каждый раз дожидаясь полного ответа,
и печатает среднее время запроса, общий объём данных и скорость скачивания.
"""

import argparse
import sys
import time

import requests

REQUESTS_COUNT = 10      # сколько запросов делаем
TIMEOUT_SECONDS = 30     # сколько максимум ждём ответ сервера


def parse_args():
    """Читает адрес из аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Замер скорости скачивания: 10 запросов к одному адресу."
    )
    parser.add_argument("url", help="адрес, к которому стучимся (например, ссылка на большую картинку)")
    return parser.parse_args()


def make_request(url):
    """Делает один запрос и возвращает (время в секундах, размер ответа в байтах)."""
    # Просим сервер не сжимать ответ, чтобы считать реальный объём данных по сети
    headers = {"Accept-Encoding": "identity"}

    start = time.perf_counter()                       # засекаем время до запроса
    response = requests.get(url, headers=headers, timeout=TIMEOUT_SECONDS)
    # Без stream=True requests сам скачивает тело ответа целиком,
    # поэтому к этой строке мы уже дождались полного ответа
    elapsed = time.perf_counter() - start             # прошло времени

    response.raise_for_status()                       # ошибка, если статус 4xx/5xx
    return elapsed, len(response.content)


def main():
    args = parse_args()

    times = []   # время каждого успешного запроса (секунды)
    sizes = []   # размер каждого успешного ответа (байты)

    print(f"Адрес: {args.url}")
    print(f"Делаю {REQUESTS_COUNT} запросов последовательно...\n")

    for i in range(1, REQUESTS_COUNT + 1):
        try:
            elapsed, size = make_request(args.url)
        except requests.RequestException as error:
            print(f"Запрос {i:>2}: ошибка — {error}")
            continue

        times.append(elapsed)
        sizes.append(size)
        print(f"Запрос {i:>2}: {elapsed:.3f} с, {size / 1_000_000:.2f} МБ")

    if not times:
        print("\nНи один запрос не удался, считать нечего.")
        sys.exit(1)

    total_time = sum(times)
    total_bytes = sum(sizes)
    average_time = total_time / len(times)

    # Скорость = всего данных / всего времени.
    # В мегабайтах в секунду и в мегабитах в секунду (1 байт = 8 бит).
    speed_mb_s = total_bytes / total_time / 1_000_000
    speed_mbit_s = speed_mb_s * 8

    print("\n--- Результат ---")
    print(f"Успешных запросов:     {len(times)} из {REQUESTS_COUNT}")
    print(f"Среднее время запроса: {average_time:.3f} с")
    print(f"Скачано данных:        {total_bytes / 1_000_000:.2f} МБ")
    print(f"Скорость скачивания:   {speed_mbit_s:.2f} Мбит/с ({speed_mb_s:.2f} МБ/с)")


if __name__ == "__main__":
    main()
