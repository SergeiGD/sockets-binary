from dataclasses import dataclass
import struct


@dataclass
class ClientRequest:
    """
    Класс для запроса клиента
    """
    command_code: int
    room: int = 0
    card: str = ''

    MASK: str = 'h i 50s'  # маска запроса. Снала идет команда (short), затем номер команты (int) и код карты (str)

    def encode(self):
        """
        Кодирование запроса для отправки
        :return: поток байтов
        """
        return struct.pack(ClientRequest.MASK, self.command_code, self.room, self.card.encode())

    @classmethod
    def decode(cls, byte_stream):
        """
        Декодирование запроса
        :param byte_stream: поток байтов
        :return: экземпляр класса ClientRequest, собранный из потока байтов
        """
        fields_tuple = struct.unpack(cls.MASK, byte_stream)
        instance = cls(
            command_code=fields_tuple[0],
            room=fields_tuple[1],
            card=fields_tuple[2].decode().rstrip('\x00'),  # убираем лишнии символы
        )
        return instance


@dataclass
class ServerResponse:
    """
    Класс для ответа сервера
    """
    success: bool
    msg: str

    MASK: str = '? 50s'  # маска отмета. Снала идет статус (bool), затем сообщение (str)

    def encode(self):
        """
        Кодирование отмета для отправки
        :return: поток байтов
        """
        return struct.pack(ServerResponse.MASK, self.success, self.msg.encode())

    @classmethod
    def decode(cls, byte_stream):
        """
        Декодирование ответа
        :param byte_stream: поток байтов
        :return: экземпляр класса ServerResponse, собранный из потока байтов
        """
        fields_tuple = struct.unpack(cls.MASK, byte_stream)
        instance = cls(
            success=fields_tuple[0],
            msg=fields_tuple[1].decode().rstrip('\x00'),  # убираем лишнии символы
        )
        return instance
