import socket
from modules.structures import ClientRequest, ServerResponse


def run_server():
    # биндим сокет и начинаем прослушивание
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 9090))
    server.listen(1)

    print('Ожидание подключения')
    client, addr = server.accept()
    print(f'Клиент {addr} подключился')

    while True:  # обслуживаем клиента, пока он не захочет первать соединение
        data = client.recv(1024)
        request = ClientRequest.decode(data)  # декодим запрос клиента
        print(f'Получен запрос {request.command_code}')

        if request.command_code == 1:  # команда привязки карты к номеру
            msg = f'Карта {request.card} привязана к номеру {request.room}'
            response = ServerResponse(success=True, msg=msg)
        if request.command_code == 2:  # команда отвязки карты от номера
            msg = f'Карта {request.card} отвязана от номера {request.room}'
            response = ServerResponse(success=True, msg=msg)
        if request.command_code == 3:  # команда отключения
            print('Сервер отключен')
            client.close()
            server.close()
            return

        client.send(response.encode())  # посылаем ответ клиенту


if __name__ == '__main__':
    run_server()

