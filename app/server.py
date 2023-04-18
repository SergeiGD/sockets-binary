import socket
from modules.structures import ClientRequest, ServerResponse
from modules.classes import Card, CardRoomPair
import redis


def run_server():
    # биндим сокет и начинаем прослушивание
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 9090))
    server.listen(1)

    redis_connection = redis.StrictRedis(
        host='localhost',
        port=6379,
        decode_responses=True,
        charset='utf-8',
    )

    print('Ожидание подключения')
    client, addr = server.accept()
    print(f'Клиент {addr} подключился')

    while True:
        # обслуживаем клиента, пока он не захочет первать соединение
        data = client.recv(1024)
        # request = ClientRequest.decode(data)  # декодим запрос клиента
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
            # команда отключения
            print('Сервер отключен')
            client.close()
            server.close()
            return

        else:
            response = ServerResponse(success=False, msg='Неопознаная комманда')

        client.send(response.encode())  # посылаем ответ клиенту


if __name__ == '__main__':
    run_server()
