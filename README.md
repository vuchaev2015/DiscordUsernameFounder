<br/>
<p align="center">
  <a href="https://github.com/vuchaev2015/DiscordUsernameFounder">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Discord Username Founder</h3>

</p>

![Downloads](https://img.shields.io/github/downloads/vuchaev2015/DiscordUsernameFounder/total) ![Issues](https://img.shields.io/github/issues/vuchaev2015/DiscordUsernameFounder) 

## Содержание

* [О проекте](#О-проекте)
* [Начало](#Начало)
  * [Требования](#Требования)
  * [Установка](#Установка)
* [Использование](#Использование)

## О проекте

![Screen Shot](https://lztcdn.com/files/16b18e892c80d23e54515534c35606a2291a68dd1f7a4cb64abf6dbbae7c4d28.webp)

Discord Username Founder - поможет вам в поиске свободных никнеймов для Discord.

## Начало

Чтобы запустить Python скрипт, выполните следующие простые шаги.

### Требования

* Python версии не ниже 3

```sh
https://www.python.org/
```

### Установка


1. Клонируйте репозиторий

```sh
git clone https://github.com/vuchaev2015/DiscordUsernameFounder.git
```

2. Установите Python модули
```sh
pip3 install -r requirements.txt 
```

## Использование

В файле usernames.txt укажите юзернеймы которые будут проверяться, в файле tokens.txt укажите токены Discord. После установки всех необходимых модулей запустите файл main.py
Если вы хотите использовать многопоток: python3 main.py -t 2 (вместо 2 указываете свое количество потоков. Количество потоков не должно превышать количество токенов)
Настройте метод работы в config.json

### Методы для работы
me - проверяет путем попытки изменения через ваш профиль
friends - проверяет путем отправки заявки в друзья Discord


