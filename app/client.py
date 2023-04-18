import socket
from modules.structures import ServerResponse, ClientRequest
from modules.classes import CardRoomPair


def run_client():
    # подключаемся к северу
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 9090))
    print('Подключение установлено')

    while True:
        print('Выберите действие:')
        print('0 - проверить доступ')
        print('1 - привязать карту к номеру')
        print('2 - отвязать карту от номера')
        print('3 - выключение')
        command = input()
        if not command.isdigit() or int(command) < 0 or int(command) > 3:
            print('Неизвестная команда')
            continue
        command = int(command)

        if command == 0 or command == 1 or command == 2:
            room_number, card_number = read_pair()  # получаем номер команты и карты

            request_body = CardRoomPair(room=room_number, card_number=card_number)
            request = ClientRequest(command_code=command, body=request_body)

        if command == 3:
            #  если запрос отключения, то кидаем только номер команлы
            request = ClientRequest(command_code=command)

        client.send(request.encode())  # отправляем запрос заэнкоженные запрос

        if command != 3:
            # если команда не 3 (отключение), то придет ответ
            data = client.recv(1024)
            response = ServerResponse.decode(data)  # декодим пришедший ответ
            print(f'Успех: {response.success}')
            print(f'Сообщение: {response.msg}')
        else:
            # иначе просто отключаемся
            print('Отключение')
            client.close()
            return


def read_pair():
    """
    Считываем номера комнаты и карты
    :return: пара номер комнаты, номер карты
    """
    room_number = input('Номер команты ')

    while not room_number.isdigit():
        print('Нвереный формат номера комнаты, необходимо число')
        room_number = input('Номер команты ')

    room_number = int(room_number)
    card_number = input('Номер карты ')

    while len(card_number) > 50:
        print('Номер карты не может содержать более 50 символов')
        card_number = input('Номер карты ')

    return room_number, card_number


if __name__ == '__main__':
    run_client()
