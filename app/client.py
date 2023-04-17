import socket
from modules.structures import ServerResponse, ClientRequest


def run_client():
    # подключаемся к северу
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 9090))
    print('Подключение установлено')

    while True:
        print('Выберите действие:')
        print('1 - привязать карту к номеру')
        print('2 - отвязать карту от номера')
        print('3 - выключение')
        command = input()
        if not command.isdigit() or int(command) < 1 or int(command) > 3:  # проверяем валидность данных
            print('Неизвестная команда')
            continue

        command = int(command)

        if command != 3:  # если команда 1 или 2, то это привязка/отвязка номера и нужны доп. данные
            room_number = input('Номер команты ')
            card_number = input('Номер карты ')

            while not room_number.isdigit():
                print('Нвереный формат номера комнаты, необходимо число')
                room_number = input('Номер команты ')

            room_number = int(room_number)

            while len(card_number) > 50:
                print('Номер карты не может содержать более 50 символов')
                card_number = input('Номер карты ')

            request = ClientRequest(command_code=command, room=room_number, card=card_number)  # генерируем запрос
        else:
            request = ClientRequest(command_code=command)  # если запрос отключения, то кидаем только номер команлы

        client.send(request.encode())  # отправляем запрос заэнкоженные запрос

        if command != 3:  # если команда 1 или 2, то придет ответ
            data = client.recv(1024)
            response = ServerResponse.decode(data)  # декодим пришедший ответ
            print(response.msg)
        else:
            print('Отключение')
            client.close()  # отключаемся
            return


if __name__ == '__main__':
    run_client()
