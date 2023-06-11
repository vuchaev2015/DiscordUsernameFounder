import requests
import time
import random
from loguru import logger

def update_username_list(username, usernames):
    usernames.remove(username)
    with open('usernames.txt', 'w') as f:
        f.write('\n'.join(usernames))

def check_username(username, token, headers):
    json_data = {
        'username': username,
        'password': '',
    }

    response = requests.patch('https://discord.com/api/v9/users/@me', headers=headers, json=json_data)
    response_json = response.json()

    if response.status_code == 400 and response_json['message'] == 'Invalid Form Body':
        errors = response_json['errors']
        if 'username' in errors:
            error_codes = [error['code'] for error in errors['username']['_errors']]
            if 'USERNAME_ALREADY_TAKEN' in error_codes:
                return 'taken'
        elif "PASSWORD_DOES_NOT_MATCH" in str(errors):
            return 'not_taken'
    elif response.status_code == 401:
        return 'unauthorized'
    elif "retry_after" in response_json:
        return 'rate_limited', response_json["retry_after"]
    else:
        return 'unknown_error'


def load_file(file_name):
    with open(file_name, 'r') as f:
        return f.read().splitlines()


def append_to_file(file_name, content):
    with open(file_name, 'a') as f:
        f.write(content + '\n')


def main():
    tokens = load_file('tokens.txt')
    usernames = load_file('usernames.txt')

    headers = {
        'authority': 'discord.com',
        'accept': '*/*',
        'accept-language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
        'content-type': 'application/json',
        'origin': 'https://discord.com',
        'referer': 'https://discord.com/channels/@me',
    }

    sleep_times = {token: 0 for token in tokens}

    valid_tokens = []

    for token in tokens:
        logger.info(f"Проверяем токен {token}")
        json_data = {
            'username': 'qwe',
            'password': '',
        }
        headers['authorization'] = token

        response = requests.patch('https://discord.com/api/v9/users/@me', headers=headers, json=json_data)
        response_json = response.json()

        if response.status_code == 401:
            logger.error(f"Токен не авторизован. Удаляем токен. Токен: {token}")
        elif 'USERNAME_ALREADY_TAKEN' in str(response_json):
            logger.success(f"Токен готов к работе. Токен: {token}")
            valid_tokens.append(token)
        elif 'USERNAME_TOO_MANY_USERS' in str(response_json):
            logger.error(f"Данному токену нельзя установить никнейм без тега. Токен: {token}")

    tokens = valid_tokens
    sleep_times = {token: 0 for token in tokens}

    for i, username in enumerate(usernames):
        if not tokens:
            logger.error("Нет валидных токенов")
            break

        token = tokens[i % len(tokens)]
        headers['authorization'] = token

        while sleep_times[token] > time.time():
            token = min(sleep_times, key=lambda t: sleep_times[t])
            headers['authorization'] = token
            time.sleep(max(0, sleep_times[token] - time.time()))

        result = check_username(username, token, headers)

        if result == 'taken':
            logger.info(f'Никнейм {username} уже используется. Токен: {token}')
            append_to_file('bad.txt', username)
            update_username_list(username, usernames)
            sleep_times[token] = time.time() + random.uniform(3, 5)

        elif result == 'not_taken':
            logger.info(f'Никнейм {username} не используется. Токен: {token}')
            append_to_file('good.txt', username)
            update_username_list(username, usernames)
            sleep_times[token] = time.time() + random.uniform(1, 3)

        elif result == 'unauthorized':
            logger.error(f"Токен не авторизован. Удаляем токен. Токен: {token}")
            tokens.remove(token)

        elif result[0] == 'rate_limited':
            logger.warning(f'Поймали Rate Limit. Спим {result[1]} секунд. Токен: {token}')
            sleep_times[token] = time.time() + result[1]

        else:
            logger.error(f"Неизвестная ошибка при никнейме: {username}. Токен: {token}")
            #append_to_file('unknown.txt', username)
            #update_username_list(username, usernames)
            sleep_times[token] = time.time() + random.uniform(5, 10)

if __name__ == "__main__":
    main()