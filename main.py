import requests
import time
import random
from loguru import logger


def update_username_list(username, usernames):
    usernames.remove(username)
    with open('usernames.txt', 'w') as f:
        f.write('\n'.join(usernames))

def check_username(username, token, headers):
    try:
        json_data = {'username': username, 'password': ''}
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
    except requests.exceptions.RequestException as e:
        return 'connection_error'

def load_file(file_name):
    with open(file_name, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def append_to_file(file_name, content):
    with open(file_name, 'a') as f:
        f.write(content + '\n')

def main():
    tokens, usernames = load_file('tokens.txt'), load_file('usernames.txt')

    if not usernames:
        logger.error("Файл usernames.txt пуст")
        input()
        return
    if not tokens:
        logger.error("Файл tokens.txt пуст")
        input()
        return

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
        headers['authorization'] = token
        connection_error = True

        while connection_error:
            try:
                response = requests.patch('https://discord.com/api/v9/users/@me', headers=headers,
                                          json={'username': 'qwe', 'password': ''})
                response_json = response.json()
                connection_error = False

                if response.status_code == 401:
                    logger.error(f"Токен {token} не авторизован и был удален")
                elif 'USERNAME_ALREADY_TAKEN' in str(response_json):
                    logger.success(f"Токен {token} готов к работе.")
                    valid_tokens.append(token)
                elif 'USERNAME_TOO_MANY_USERS' in str(response_json):
                    logger.error(f"Для токена {token} нельзя установить имя пользователя без тега")

            except requests.exceptions.RequestException:
                logger.warning(
                    f"Ошибка соединения при проверке токена: {token}. Повторяем проверку через 10 секунд.")
                time.sleep(10)

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
            logger.info(f'Никнейм {username} уже используется.')
            append_to_file('bad.txt', username)
            update_username_list(username, usernames)
            sleep_times[token] = time.time() + random.uniform(3, 5)

        elif result == 'not_taken':
            logger.info(f'Никнейм {username} не используется.')
            append_to_file('good.txt', username)
            update_username_list(username, usernames)
            sleep_times[token] = time.time() + random.uniform(1, 3)

        elif result == 'unauthorized':
            logger.error(f"Токен {token} не авторизован и был удален")
            tokens.remove(token)

        elif result[0] == 'rate_limited':
            logger.warning(f'Токен {token} поймал Rate Limit. Спим {result[1]} секунд. ')
            sleep_times[token] = time.time() + result[1]

        elif result == 'connection_error':
            logger.warning(f"Ошибка соединения. Повторяем запрос через 10 секунд.")
            time.sleep(10)

        else:
            logger.error(f"Неизвестная ошибка: {result}")
            sleep_times[token] = time.time() + random.uniform(5, 10)

    if not usernames:
        logger.success("Работа завершена. Никнеймов для проверки больше нет.")
        input()

if __name__ == "__main__":
    main()
