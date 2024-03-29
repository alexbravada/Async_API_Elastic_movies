# ССЫЛКА НА РЕПОЗИТОРИЙ https://github.com/alexbravada/Async_API_sprint_2/
# инвайт был предоставлен аккаунту blue deep
# Проектная работа 5 спринта

**ВАЖНО:** предполагается, что на момент запуска имеется образ базы данных из предыдущего спринта,
заполненный данными 

**ВАЖНО:** в папке ETL располагается реализация одноименного сервиса, в том числе, из предыдущего
спринта.

## Порядок запуска:
1. Копируем из репозитория папку с проектом
2. Запуск ETL-процесса из файла ./ETL/main.py
3. Запуск подготовленного приложения

```shell
docker-compose up -d --build
```
## Запуск тестов:
```shell
pytest ./tests/functional/src
```











# python -m uvicorn main:app --port=8106 --reload 
Запуск приложения через терминал.

**Важное сообщение для тимлида:** для ускорения проверки проекта укажите ссылку на приватный репозиторий с командной работой в файле readme и отправьте свежее приглашение на аккаунт [BlueDeep](https://github.com/BigDeepBlue).

В папке **tasks** ваша команда найдёт задачи, которые необходимо выполнить в первом спринте второго модуля.  Обратите внимание на задачи **00_create_repo** и **01_create_basis**. Они расцениваются как блокирующие для командной работы, поэтому их необходимо выполнить как можно раньше.

Мы оценили задачи в стори поинтах, значения которых брались из [последовательности Фибоначчи](https://ru.wikipedia.org/wiki/Числа_Фибоначчи) (1,2,3,5,8,…).

Вы можете разбить имеющиеся задачи на более маленькие, например, распределять между участниками команды не большие куски задания, а маленькие подзадачи. В таком случае не забудьте зафиксировать изменения в issues в репозитории.

**От каждого разработчика ожидается выполнение минимум 40% от общего числа стори поинтов в спринте.**
