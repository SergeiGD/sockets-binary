from dataclasses import dataclass
from .classes import IBinary
from .response_codes import ResponseCodes
import bitstring


@dataclass
class ClientRequest:
    """
    Класс для запроса клиента
    """
    command_code: int
    body: IBinary | None = None
    MASK: str = 'uint4'  # базовая маска команды запроса

    def encode(self):
        """
        Кодирование запроса для отправки
        :return: поток байтов
        """
        if self.body is not None:
            request_encoded = bitstring.pack(self.MASK, self.command_code)  # кодируем команду запроса
            body_encoded = self.body.encode()  # кодируем тело запроса
            request_encoded.append(body_encoded)
            return request_encoded.bytes
        else:
            # если нету тела, то возвращаем просто код запроса
            request_encoded = bitstring.pack('uint8', self.command_code)  # uint8 т.к. должно быть кратно 8
            return request_encoded.bytes

    @classmethod
    def decode(cls, byte_stream):
        """
        Декоридрование запроса
        :param byte_stream: поток байтов
        :return: команда запроса и закодированное тело
        """
        bit_stream = bitstring.BitStream(byte_stream)  # преобразуем в биты
        if len(bit_stream) > 8:
            # если есть тело, то возращем команду вместе с телом
            command = bit_stream.read(4).uint  # если есть тело, то первые 4 бита - код запроса
            return command, bit_stream[4:]
        else:
            # иначе только команду
            command = bit_stream.read(8).uint  # если нет тела, то весь первый байт код запроса
            return command, None


@dataclass
class ServerResponse:
    """
    Класс для ответа сервера
    """
    success: bool
    code: ResponseCodes

    MASK: str = 'bool, uint7'  # маска ответа. Снала идет статус, затем код ответа (uint7 чтоб было кратно 8)

    def encode(self):
        """
        Кодирование отмета для отправки
        :return: поток байтов
        """
        return bitstring.pack(self.MASK, self.success, self.code.value).bytes

    @classmethod
    def decode(cls, byte_stream):
        """
        Декодирование ответа
        :param byte_stream: поток байтов
        :return: экземпляр класса ServerResponse, собранный из потока байтов
        """
        bit_stream = bitstring.BitStream(byte_stream)  # преобразуем в биты
        return cls(
            success=bit_stream.read(1).bool,
            code=ResponseCodes(bit_stream.read(7).uint),
        )
