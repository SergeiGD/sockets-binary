import socket
from modules.structures import ServerResponse, ClientRequest
from modules.classes import CardRoomPair, Card
import struct


def run_client():
    # подключаемся к северу
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 9090))
    print('Подключение установлено')

    while True:
        print('0 - проверить доступ')
        print('1 - активировать карту')
        print('2 - деактивировать карту')
        print('3 - привязать карту к номеру')
        print('4 - отвязать карту к номера')
        print('5 - выключение сервера')
        print('6 - отключится')
        command = input('Выберите действие: ')
        if not command.isdigit() or int(command) < 0 or int(command) > 6:
            print('Неизвестная команда')
            continue
        command = int(command)

        if command == 0:
            # команда проверки доступа
            room_number = read_room_number()  # получаем номер команты
            card_number = read_card_number()  # получаем номер карты

            request_body = CardRoomPair(room=room_number, card_number=card_number)
            request = ClientRequest(command_code=command, body=request_body)

        if command == 1:
            # команда активации карты
            card_number = read_card_number()  # получаем номер карты
            card_ttl = read_time_to_live()  # получаем номер карты
            request_body = Card(card_number=card_number, time_to_live=card_ttl)
            request = ClientRequest(command_code=command, body=request_body)

        if command == 2:
            # команда деактивации карты
            card_number = read_card_number()  # получаем номер карты
            request_body = Card(card_number=card_number)
            request = ClientRequest(command_code=command, body=request_body)

        if command == 3 or command == 4:
            # команда привязк карты к номеру/отвязки карты от номера
            room_number = read_room_number()  # получаем номер команты
            card_number = read_card_number()  # получаем номер карты

            request_body = CardRoomPair(room=room_number, card_number=card_number)
            request = ClientRequest(command_code=command, body=request_body)

        if command == 5 or command == 6:
            #  если запрос выключение сервера/отключения, то кидаем только номер команлы
            request = ClientRequest(command_code=command)

        client.send(request.encode())  # отправляем заэнкоженные запрос

        if command != 5 and command != 6:
            # если команда не 5/6 (отключение/выключение), то придет ответ
            data = client.recv(1024)
            try:
                response = ServerResponse.decode(data)  # декодим пришедший ответ
            except struct.error:
                print('Ошибка при получении ответа. Похоже, сервер не активен')
                client.close()
                return
            print(f'Успех: {response.success}')
            print(f'Сообщение: {response.msg}')
        else:
            # иначе просто отключаемся
            print('Отключение')
            client.close()
            return


def read_room_number() -> int:
    """
    Считывание номера комнаты
    :return: номер комнаты
    """
    room_number = input('Номер команты: ')

    while not room_number.isdigit():
        print('Нвереный формат номера комнаты, необходимо число')
        room_number = input('Номер команты ')

    return int(room_number)


def read_card_number() -> str:
    """
    Считывание номера карты
    :return: номер карты
    """
    card_number = input('Номер карты: ')

    while len(card_number) > 50:
        print('Номер карты не может содержать более 50 символов')
        card_number = input('Номер карты ')

    return card_number


def read_time_to_live() -> int:
    """
    Считывание времени дейтсвия карты
    :return: время действия карты
    """
    time_to_live = input('Время действия (в днях): ')

    while not time_to_live.isdigit() or int(time_to_live) < 1:
        print('Время действия должно быть числом меньше 1')
        time_to_live = input('Время действия (в днях) ')

    seconds_in_day = 86400  # т.к. редис хранит TTL в секундах, сразу приведем к ним
    time_to_live = int(time_to_live) * seconds_in_day

    return time_to_live


if __name__ == '__main__':
    run_client()
