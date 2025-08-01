import requests

import os
from dotenv import load_dotenv
load_dotenv()
IP = os.getenv('IP')


def create_or_update_user(telegram_id, name_telegram):
    data = {
        "id_telegram": telegram_id,
        "name_telegram": name_telegram,
    }

    try:
        response = requests.post(f"http://{IP}/zaek/api/zaek-user/", json=data)
        response.raise_for_status()  # Проверка на HTTP-ошибки
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def get_question():
    try:
        response = requests.get(f"http://{IP}/zaek/api/zaek-question/")
        response.raise_for_status()  # Проверка на HTTP-ошибки
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


async def update_user_statistic(telegram_id: str, is_correct: bool):
    api_url = f"http://{IP}/zaek/api/update_stats/"
    data = {
        "telegram_id": telegram_id,
        "is_correct": is_correct
    }
    try:
        response = requests.post(api_url, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при обновлении статистики: {e}")
        return None