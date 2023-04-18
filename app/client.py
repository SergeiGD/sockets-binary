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
        print('1 - деактивировать карту')
        print('2 - привязать карту к номеру')
        print('3 - создать карту сотрудника')
        print('4 - выключение сервера')
        print('5 - отключится')
        command = input('Выберите действие: ')
        if not command.isdigit() or int(command) < 0 or int(command) > 5:
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
            # команда деактивации карты
            card_number = read_card_number()  # получаем номер карты
            request_body = Card(card_number=card_number)
            request = ClientRequest(command_code=command, body=request_body)

        if command == 2:
            # команда привязки карты к номеру
            room_number = read_room_number()  # получаем номер команты
            card_number = read_card_number()  # получаем номер карты
            time_to_live = read_time_to_live()  # получаем TTL карты

            request_body = CardRoomPair(room=room_number, card_number=card_number, time_to_live=time_to_live)
            request = ClientRequest(command_code=command, body=request_body)

        if command == 3:
            # команда создания карты сотрудника
            card_number = read_card_number()  # получаем номер карты
            time_to_live = read_time_to_live()  # получаем TTL карты

            request_body = Card(card_number=card_number, time_to_live=time_to_live)
            request = ClientRequest(command_code=command, body=request_body)

        if command == 4 or command == 5:
            #  если запрос выключение сервера/отключения, то кидаем только номер команлы
            request = ClientRequest(command_code=command)

        client.send(request.encode())  # отправляем заэнкоженные запрос

        if command != 4 and command != 5:
            # если команда не 4/5 (отключение/выключение), то придет ответ
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


def read_room_number():
    """
    Считываем номера комнаты и карты
    :return: пара номер комнаты, номер карты
    """
    room_number = input('Номер команты: ')

    while not room_number.isdigit():
        print('Нвереный формат номера комнаты, необходимо число')
        room_number = input('Номер команты ')

    return int(room_number)


def read_card_number():
    card_number = input('Номер карты: ')

    while len(card_number) > 50:
        print('Номер карты не может содержать более 50 символов')
        card_number = input('Номер карты ')

    return card_number


def read_time_to_live():
    time_to_live = input('Время действия (в днях): ')

    while not time_to_live.isdigit() and int(time_to_live) < 1:
        print('Время действия не может быть меньше 1 дня')
        time_to_live = input('Время действия (в днях) ')

    seconds_in_day = 86400  # т.к. редис хранит TTL в секундах, сразу приведем к ним
    time_to_live = int(time_to_live) * seconds_in_day

    return time_to_live


if __name__ == '__main__':
    run_client()
