import signal
import socket
from modules.structures import ClientRequest, ServerResponse
from modules.classes import Card, CardRoomPair
import redis
import os
import threading
from redis import Redis


PID_FILE = '.pid'
pid = os.getpid()
active_sockets = []


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
                response = ServerResponse(success=True, msg='Доступ разрешен')
            else:
                response = ServerResponse(success=False, msg='Доступ запрещен')

        elif request_code == 1:
            # команда активации карты
            card = Card.decode(encoded_body)
            if redis_connection.exists(card.card_number):
                msg = 'Эта карта уже активирована'
                response = ServerResponse(success=False, msg=msg)
            else:
                # добавляем элемент с пустым значением (т.к. сет не может быть пустым)
                redis_connection.sadd(card.card_number, '')
                redis_connection.expire(card.card_number, card.time_to_live)
                msg = f'Карта {card.card_number} активироана'
                response = ServerResponse(success=True, msg=msg)

        elif request_code == 2:
            # команда деактивации карты
            card = Card.decode(encoded_body)
            redis_connection.delete(card.card_number)  # удаляем ключ
            msg = f'Карта {card.card_number} деактивироана'
            response = ServerResponse(success=True, msg=msg)

        elif request_code == 3:
            # команда привязки карты к номеру
            pair = CardRoomPair.decode(encoded_body)
            if not redis_connection.exists(pair.card_number):
                msg = 'Эта карта не активирована'
                response = ServerResponse(success=False, msg=msg)
            else:
                redis_connection.sadd(pair.card_number, pair.room)  # добавляем элемент к множеству
                msg = f'Карта {pair.card_number} привязана к номеру {pair.room}'
                response = ServerResponse(success=True, msg=msg)

        elif request_code == 4:
            # команда отвязки карты от номера
            pair = CardRoomPair.decode(encoded_body)
            redis_connection.srem(pair.card_number, pair.room)  # удаляем элемент из множества
            msg = f'Карта {pair.card_number} отвязана от номера {pair.room}'
            response = ServerResponse(success=True, msg=msg)

        elif request_code == 5:
            # команда выключения сервера
            print('Получена команда отключения')
            try:
                os.remove(PID_FILE)  # удаляем файл, это сигнал к отключения сервера
            except OSError:
                pass
            return
        elif request_code == 6:
            # команда отключения клиента
            print(f'Клиент {addr} отключился')
            client.close()
            active_sockets.remove(client)  # удаляем из активных сокетов
            return
        else:
            response = ServerResponse(success=False, msg='Неопознаная комманда')

        client.send(response.encode())  # посылаем ответ клиенту


def run_server():
    """
    Запуск сервера
    :return:
    """
    redis_connection = redis.StrictRedis(
        host='localhost',
        port=6379,
        decode_responses=True,
        charset='utf-8',
    )

    # биндим сокет и начинаем прослушивание
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    active_sockets.append(server)
    server.bind(('localhost', 9090))
    server.listen(5)
    print('Ожидание подключения')

    while True:
        client, addr = server.accept()
        active_sockets.append(client)
        print(f'Клиент {addr} подключился')
        # запускаем взаимодейтсвие в новом потоке
        threading.Thread(target=client_listener, args=(client, addr, redis_connection)).start()


def pid_file_listener():
    """
    Прослушиватель .pid файла, отключает все соединения при его удалении
    :return:
    """
    while os.path.isfile(PID_FILE):
        pass  # ожидаем удаления файла
    print('.pid файл удален, выключение...')
    for i in active_sockets:
        i.close()  # закрываем сокеты
    os.kill(pid, signal.SIGTERM)  # убиваем процесс


if __name__ == '__main__':
    with open(PID_FILE, 'w') as pid_file:
        pid_file.write(str(pid))
    threading.Thread(target=pid_file_listener).start()
    run_server()
