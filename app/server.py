import socket
from modules.structures import ClientRequest, ServerResponse
from modules.classes import Card, CardRoomPair


def run_server():
    # биндим сокет и начинаем прослушивание
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 9090))
    server.listen(1)

    print('Ожидание подключения')
    client, addr = server.accept()
    print(f'Клиент {addr} подключился')

    while True:
        # обслуживаем клиента, пока он не захочет первать соединение
        data = client.recv(1024)
        request_code, encoded_body = ClientRequest.decode(data)  # декодим запрос клиента
        print(f'Получен запрос {request_code}')

        if request_code == 0:
            # команда регистрации карточки
            card = Card.decode(encoded_body)  # декоридруем тело запроса
            msg = f'Карта {card.card_number} успешно зарегестрирована'
            response = ServerResponse(success=True, msg=msg)

        elif request_code == 1:
            # команда привязки карты к номеру
            card_room = CardRoomPair.decode(encoded_body)  # декоридруем тело запроса
            msg = f'Карта {card_room.card_number} привязана к номеру {card_room.room}'
            response = ServerResponse(success=True, msg=msg)

        elif request_code == 2:
            # команда отвязки карты от номера
            card_room = CardRoomPair.decode(encoded_body)  # декоридруем тело запроса
            msg = f'Карта {card_room.card_number} отвязана от номера {card_room.room}'
            response = ServerResponse(success=True, msg=msg)

        elif request_code == 3:
            # команда отключения
            print('Сервер отключен')
            client.close()
            server.close()
            return

        else:
            msg = 'Неопознаная комманда'
            response = ServerResponse(success=False, msg=msg)

        client.send(response.encode())  # посылаем ответ клиенту


if __name__ == '__main__':
    run_server()

