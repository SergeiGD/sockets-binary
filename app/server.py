import signal
import socket
from modules.structures import ClientRequest, ServerResponse
from modules.classes import Card, CardRoomPair
import redis
import os
import threading


PID_FILE = '.pid'
pid = os.getpid()
active_sockets = []


def client_listen(client, addr, redis_connection):
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
            if redis_connection.hget(pair.card_number, 'room') == str(pair.room) or \
                    redis_connection.hexists(pair.card_number, 'is_super_card'):
                response = ServerResponse(success=True, msg='Доступ разрешен')
            else:
                response = ServerResponse(success=False, msg='Доступ запрещен')

        elif request_code == 1:
            # команда деактивации карты
            card = Card.decode(encoded_body)
            redis_connection.delete(card.card_number)  # удаляем из редиса
            msg = f'Карта {card.card_number} деактивироана'
            response = ServerResponse(success=True, msg=msg)

        elif request_code == 2:
            # команда привязки карты к номеру
            pair = CardRoomPair.decode(encoded_body)
            if redis_connection.exists(pair.card_number):
                # чтоб не перезаписывать уже имеющиеся данные, кидаем отказ
                msg = 'Эта карта уже активирована сначала'
                response = ServerResponse(success=False, msg=msg)
            else:
                redis_connection.hset(pair.card_number, mapping={
                    'room': pair.room
                })
                redis_connection.expire(pair.card_number, pair.time_to_live)  # устанавливаем TTL записи
                msg = f'Карта {pair.card_number} привязана к номеру {pair.room}'
                response = ServerResponse(success=True, msg=msg)

        elif request_code == 3:
            # команда создания карты сотрудника
            card = Card.decode(encoded_body)
            if redis_connection.exists(card.card_number):
                # чтоб не перезаписывать уже имеющиеся данные, кидаем отказ
                msg = 'Эта карта уже активирована'
                response = ServerResponse(success=False, msg=msg)
            else:
                redis_connection.hset(card.card_number, mapping={
                    'is_super_card': 1
                })
                redis_connection.expire(card.card_number, card.time_to_live)  # устанавливаем TTL записи
                msg = f'Карта сотрудника {card.card_number} создана'
                response = ServerResponse(success=True, msg=msg)

        elif request_code == 4:
            # команда выключения сервера
            print('Получена команда выключения')
            try:
                os.remove(PID_FILE)  # удаляем файл, это сигнал к отключения сервера
            except OSError:
                pass
            return
        elif request_code == 5:
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
        threading.Thread(target=client_listen, args=(client, addr, redis_connection)).start()


def pid_file_listener():
    """
    Прослушиватель .pid файла, отключает все соединения при его удалении
    :return:
    """
    while os.path.isfile(PID_FILE):
        pass
    print('.pid файл удален, выключение...')
    for i in active_sockets:
        i.close()
    os.kill(pid, signal.SIGTERM)


if __name__ == '__main__':
    with open(PID_FILE, 'w') as pid_file:
        pid_file.write(str(pid))
    threading.Thread(target=pid_file_listener).start()
    run_server()
