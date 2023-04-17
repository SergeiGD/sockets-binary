import socket
from modules.structures import ServerResponse, ClientRequest
from modules.classes import Card, CardRoomPair


def run_client():
    # подключаемся к северу
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 9090))
    print('Подключение установлено')

    while True:
        print('Выберите действие:')
        print('0 - зарегестрировать карту')
        print('1 - привязать карту к номеру')
        print('2 - отвязать карту от номера')
        print('3 - выключение')
        command = input()
        if not command.isdigit() or int(command) < 0 or int(command) > 3:
            print('Неизвестная команда')
            continue

        command = int(command)

        if command == 0:
            card_number = input('Номер карты ')
            while len(card_number) > 50:
                print('Номер карты не может содержать более 50 символов')
                card_number = input('Номер карты ')

            is_super_card = input('Зарегестрировать как суперкарту? (y - да) ')
            if is_super_card == 'y':
                is_super_card = True
            else:
                is_super_card = False

            request_body = Card(card_number=card_number, is_super_card=is_super_card)
            request = ClientRequest(command_code=command, body=request_body)

        if command == 1 or command == 2:
            # если команда 1 или 2, то это привязка/отвязка номера и номер карты и команты
            room_number = input('Номер команты ')
            card_number = input('Номер карты ')

            while not room_number.isdigit():
                print('Нвереный формат номера комнаты, необходимо число')
                room_number = input('Номер команты ')

            room_number = int(room_number)

            while len(card_number) > 50:
                print('Номер карты не может содержать более 50 символов')
                card_number = input('Номер карты ')

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
            print(response.msg)
        else:
            # иначе просто отключаемся
            print('Отключение')
            client.close()
            return


if __name__ == '__main__':
    run_client()
