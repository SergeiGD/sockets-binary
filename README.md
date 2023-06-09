# sockets-binary

## Описание проекта

Проект создан в учебных целях

В данном репозитории реализовано имитация работы механизма открытия двери с помощью смарт карты. Клиент может отправить серверу один из следующий запросов:
- Проверить, может ли карта открывать дверь
- Зарегестрировать карту
- Деактивировать карты
- Добавить привязать карту к комнате
- Отвязать карту от комнаты
- Отключиться
- Выключить сервер

Взамодействие происходит с помощью сокетов, клиент формирует запрос, который кодируется в последовательность бит, затем преобразуется в байты и отправляется серверу, сервер при получение запроса декодирует его и отправляет ответ клиенту. В запросе содержиться код команды (из него сервер понимает, что ему делать) и необязательное тело запроса, в котором содержится доп. информации на подобие номеру комнаты и смарт карты.

Для контроля запуска только одного экзмепляра сервера используется мьютекс.

Для возможности обслуживания сразу нескольких клиентов используется многопоточность.

При запуске сервер создает .pid файл, в который записывает свой pid, удаление этого файла сигнализуется серверу, что ему необходимо выключится.

Для хранения данных о смарт картах и номерах, которые они открывают используется Redis. Для каждой карты создается ключ с ее номером, а в качестве значений используется множество номеров комнат, которые они может открывать. Время активности карты устанавливается с помощью TTL ключа.

## Описание структуры сообщений:

**Запрос клиента: макс вес – 3 байта, мин вес – 1 байт. Состоит из:**
1)  Команда запроса (что делать) – целочисленное положительное число, вес 4 бита если есть тело, 8 бит если нет тела
2)  Необязательное тело запроса, есть три вида: пара карточка-комната, пара карточка-ttl и карточка

**Пара карточка-номер: вес 20 бит. Состоит из:**
1)  Номер карточки - целочисленное положительное число, вес 10 бит
2)  Номер комнаты -  целочисленное положительное число, вес 10 бит

**Пара карточка-ttl: макс вес 20 бит. Состоит из:**
1)  Номер карточки - целочисленное положительное число, вес 10 бит
2)  TTL (время действия карточки) - целочисленное положительное число, вес 10 бит

**Карточка: вес 12 бит. Состоит из:**
1) Номер карточки - целочисленное положительное число, вес 12 бит

**Ответ сервера: вес – 1 байт. Состоит из:**
1)  Флаг успеха – булево значение, вес 1 бит
2)  Код ответа - целочисленное положительное число, вес 7 бит