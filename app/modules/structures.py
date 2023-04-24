from dataclasses import dataclass
import struct
from .classes import IBinary


@dataclass
class ClientRequest:
    """
    Класс для запроса клиента
    """
    command_code: int
    body: IBinary | None = None
    MASK: str = 'B'  # базовая маска команды запроса

    def encode(self):
        """
        Кодирование запроса для отправки
        :return: поток байтов
        """
        request_encoded = bytearray(struct.pack(self.MASK, self.command_code))  # кодируем команду запроса

        if self.body is not None:
            body_encoded = self.body.encode()  # кодируем тело запроса, если оно есть
            request_encoded.extend(body_encoded)
        return request_encoded

    @classmethod
    def decode(cls, byte_stream):
        """
        Декоридрование запроса
        :param byte_stream: поток байтов
        :return: команда запроса и заенкоденно тело
        """
        command = struct.unpack(cls.MASK, byte_stream[0:1])[0]  # т.к. command_code это char, то это первый байт
        return command, byte_stream[1:]


@dataclass
class ServerResponse:
    """
    Класс для ответа сервера
    """
    success: bool
    msg: str

    MASK: str = '? 50s'  # маска ответа. Снала идет статус (bool), затем сообщение (str)

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
        return cls(
            success=fields_tuple[0],
            msg=fields_tuple[1].decode().rstrip('\x00'),  # убираем лишнии символы
        )
