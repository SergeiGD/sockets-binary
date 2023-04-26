import signal
import socket
from modules.structures import ClientRequest, ServerResponse
from modules.classes import Card, CardRoomPair, CardTtlPair
from modules.response_codes import ResponseCodes
import redis
import os
import threading
from redis import Redis
import posix_ipc


PID_FILE = '.pid'
SEMAPHORE_NAME = 'server_mutex'
SERVER_HOST = 'localhost'
SERVER_PORT = 9090
REDIS_PORT = 6379


def exit_program():
    """
    Корректный выход из программы
    :return:
    """
    for i in active_sockets:
        i.close()  # закрываем сокеты
    semaphore.release()  # освобождаем семафор
    semaphore.close()
    os.kill(pid, signal.SIGTERM)  # убиваем процесс


def remove_pid_file(*args, **kwargs):
    """
    Удаление pid файла (ведет к выходу из программы)
    :param args:
    :param kwargs:
    :return:
    """
    if args:
        # если есть ошибки, то выводим их
        print(args)

    try:
        os.remove(PID_FILE)  # удаляем .pid файл
    except OSError:
        pass


def pid_file_listener():
    """
    Прослушиватель .pid файла, выходит из программы при его удалении
    :return:
    """
    while os.path.isfile(PID_FILE):
        pass  # ожидаем удаления файла
    print('.pid файл удален, выключение...')
    exit_program()


def stop_signals_handler(signum, frame):
    """
    Обработчик сигналов выключения (при выходе черех CTRL + C)
    :param signum:
    :param frame:
    :return:
    """
    remove_pid_file()


def client_listener(client: socket, addr: tuple[str, int], redis_connection: Redis):
    """
    Обслуживание запросов клиента
    :param client: сокет клиента
    :param addr:  адрес клиента
    :param redis_connection:  подключение к редис
    :return:
    """
    while True:
        # обслуживаем клиента, пока он не захочет первать соединение
        data = client.recv(1024)
        request_code, encoded_body = ClientRequest.decode(data)  # декодим запрос клиента
        print(f'Получен запрос {request_code}')

        if request_code == 0:
            # команда проверки доступа
            pair = CardRoomPair.decode(encoded_body)
            if redis_connection.sismember(pair.card_number, pair.room):
                response = ServerResponse(success=True, code=ResponseCodes.OK)
            else:
                response = ServerResponse(success=False, code=ResponseCodes.ACCESS_DENIED)

        elif request_code == 1:
            # команда активации карты
            card = CardTtlPair.decode(encoded_body)
            if redis_connection.exists(card.card_number):
                response = ServerResponse(success=False, code=ResponseCodes.ALREADY_ACTIVE)
            else:
                # добавляем элемент с пустым значением (т.к. сет не может быть пустым)
                redis_connection.sadd(card.card_number, '')
                seconds_in_day = 86400  # редис хранит TTL в секундах, а приходят дни, так что преобразуем к секундам
                time_to_live = int(card.time_to_live) * seconds_in_day
                redis_connection.expire(card.card_number, time_to_live)
                response = ServerResponse(success=True, code=ResponseCodes.OK)

        elif request_code == 2:
            # команда деактивации карты
            card = Card.decode(encoded_body)
            redis_connection.delete(card.card_number)  # удаляем ключ
            response = ServerResponse(success=True, code=ResponseCodes.OK)

        elif request_code == 3:
            # команда привязки карты к номеру
            pair = CardRoomPair.decode(encoded_body)
            if not redis_connection.exists(pair.card_number):
                response = ServerResponse(success=False, code=ResponseCodes.INACTIVE)
            else:
                redis_connection.sadd(pair.card_number, pair.room)  # добавляем элемент к множеству
                response = ServerResponse(success=True, code=ResponseCodes.OK)

        elif request_code == 4:
            # команда отвязки карты от номера
            pair = CardRoomPair.decode(encoded_body)
            redis_connection.srem(pair.card_number, pair.room)  # удаляем элемент из множества
            msg = f'Карта {pair.card_number} отвязана от номера {pair.room}'
            response = ServerResponse(success=True, code=ResponseCodes.OK)

        elif request_code == 5:
            # команда выключения сервера
            print('Получена команда отключения')
            remove_pid_file()  # удаление pid файла заставляет программу выключатсья
            return
        elif request_code == 6:
            # команда отключения клиента
            print(f'Клиент {addr} отключился')
            client.close()
            active_sockets.remove(client)  # удаляем из активных сокетов
            return
        else:
            response = ServerResponse(success=False, code=ResponseCodes.UNKNOWN_COMMAND)

        client.send(response.encode())  # посылаем ответ клиенту


def run_server():
    """
    Запуск сервера
    :return:
    """
    redis_connection = redis.StrictRedis(
        host='localhost',
        port=REDIS_PORT,
        decode_responses=True,
        charset='utf-8',
    )

    # биндим сокет и начинаем прослушивание
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # помечаем как переиспользуемый
    active_sockets.append(server)
    server.bind((SERVER_HOST, SERVER_PORT))
    server.listen(5)
    print('Ожидание подключения')

    while True:
        try:
            client, addr = server.accept()
        except socket.error:
            break
        active_sockets.append(client)
        print(f'Клиент {addr} подключился')
        # запускаем взаимодейтсвие в новом потоке
        threading.Thread(target=client_listener, args=(client, addr, redis_connection)).start()


if __name__ == '__main__':
    try:
        # создаем семафор, если его нету
        semaphore = posix_ipc.Semaphore(SEMAPHORE_NAME, posix_ipc.O_CREX, initial_value=1)
    except posix_ipc.ExistentialError:
        # иначе активируем уже имеющийся
        semaphore = posix_ipc.Semaphore(SEMAPHORE_NAME)
    semaphore.acquire()  # ставим блокировку

    pid = os.getpid()
    with open(PID_FILE, 'w') as pid_file:
        pid_file.write(str(pid))  # записываем id процесса в файл

    # вешаем обработчики при выходе через CTRL + C
    signal.signal(signal.SIGINT, stop_signals_handler)

    threading.excepthook = remove_pid_file  # отлавливаем исключения в потоках для корректного выхода из программы
    threading.Thread(target=pid_file_listener).start()  # просушивание .pid файла
    active_sockets = []  # список активный сокетов (будут отключены при выходе из программы)
    run_server()  # запускаем сервер
