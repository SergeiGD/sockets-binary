import socket
from modules.structures import ClientRequest, ServerResponse
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
        request = ClientRequest.decode(data)  # декодим запрос клиента
        print(f'Получен запрос {request.command_code}')

        if request.command_code == 0:
            # команда проверки доступа
            if redis_connection.sismember(request.body.card_number, request.body.room):
                response = ServerResponse(success=True, msg='Доступ разрешен')
            else:
                response = ServerResponse(success=False, msg='Доступ запрещен')

        elif request.command_code == 1:
            # команда привязки карты к номеру
            redis_connection.sadd(request.body.card_number, request.body.room)
            msg = f'Карта {request.body.card_number} привязана к номеру {request.body.room}'
            response = ServerResponse(success=True, msg=msg)

        elif request.command_code == 2:
            # команда отвязки карты от номера
            redis_connection.srem(request.body.card_number, 1, request.body.room)
            msg = f'Карта {request.body.card_number} отвязана от номера {request.body.room}'
            response = ServerResponse(success=True, msg=msg)

        elif request.command_code == 3:
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
