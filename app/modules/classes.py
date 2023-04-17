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
class Card(IBinary):
    """
    Класс, представляющий собой карточки доступа
    """
    card_number: str
    is_super_card: bool
    MASK: str = f'50s ?'  # маска для кодирования карточки. Сначала номер карточки (str), затем суперкарта bool

    def encode(self):
        return struct.pack(self.MASK, self.card_number.encode(), self.is_super_card)

    @classmethod
    def decode(cls, byte_stream):
        fields = struct.unpack(cls.MASK, byte_stream)
        return cls(
            card_number=fields[0].decode().rstrip('\x00'),  # убираем лишнии символы
            is_super_card=fields[1],
        )


@dataclass
class CardRoomPair(IBinary):
    """
    Класс, представляющий собой пару карточки-команата
    """
    card_number: str
    room: int
    MASK: str = f'50s i' # маска для пары номер-комната. Сначала номер карточки (str), затем комната (int)

    def encode(self):
        return struct.pack(self.MASK, self.card_number.encode(), self.room)

    @classmethod
    def decode(cls, byte_stream):
        fields = struct.unpack(cls.MASK, byte_stream)
        return cls(
            card_number=fields[0].decode().rstrip('\x00'),  # убираем лишнии символы
            room=fields[1],
        )
