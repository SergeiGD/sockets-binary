from dataclasses import dataclass
import struct
from abc import ABC, abstractmethod


class IBinary(ABC):
    """
    Интерфейс для объектов, которые можно кодировать и декодировать, чтоб отправлять в запросе
    """
    @abstractmethod
    def encode(self):
        pass

    @classmethod
    @abstractmethod
    def decode(cls, byte_stream):
        pass


@dataclass
class CardRoomPair(IBinary):
    """
    Класс, представляющий собой пару карточки-команата
    """
    card_number: str
    room: int
    time_to_live: int | None = None
    MASK: str = f'50s i'  # базовая маска для пары карточка-комната. Сначала номер карточки (str), затем комната (int)

    def encode(self):
        encoded_pair = bytearray(struct.pack(self.MASK, self.card_number.encode(), self.room))
        if self.time_to_live is not None:
            encoded_pair.extend(struct.pack('l', self.time_to_live))
        return encoded_pair

    @classmethod
    def decode(cls, byte_stream):
        base_fields = struct.unpack(cls.MASK, byte_stream[0:56])  # первый 56 байтов - это карточка и номер
        instance = cls(
            card_number=base_fields[0].decode().rstrip('\x00'),  # убираем лишнии символы
            room=base_fields[1],
        )
        if len(byte_stream) > 56:
            time_to_live = struct.unpack('l', byte_stream[56:])[0]  # если есть еще байты, то это TTL
            instance.time_to_live = time_to_live
        return instance


@dataclass
class Card(IBinary):
    """
    Класс, представляющий собой карточку
    """
    card_number: str
    time_to_live: int | None = None
    MASK: str = f'50s'  # базовая маска для карточки

    def encode(self):
        encoded_pair = bytearray(struct.pack(self.MASK, self.card_number.encode()))  # кодируем номер карточки
        if self.time_to_live is not None:
            # если есть TTL, то дополнительно кодируем его
            encoded_pair.extend(struct.pack('l', self.time_to_live))
        return encoded_pair

    @classmethod
    def decode(cls, byte_stream):
        card_number = struct.unpack(cls.MASK, byte_stream[0:50])[0]  # первый 50 байт - карточка номера
        instance = cls(
            card_number=card_number.decode().rstrip('\x00'),  # убираем лишнии символы
        )
        if len(byte_stream) > 50:
            time_to_live = struct.unpack('l', byte_stream[50:])[0]  # если есть еще байты, то это TTL
            instance.time_to_live = time_to_live
        return instance
