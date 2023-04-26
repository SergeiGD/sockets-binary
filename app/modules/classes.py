from dataclasses import dataclass
from abc import ABC, abstractmethod
import bitstring
from typing import ClassVar


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
    Класс, представляющий собой пару карточка-команата
    """
    card_number: int
    room: int
    MASK: ClassVar[str] = 'uint10, uint10'  # маска для пары карточка-комната

    def encode(self):
        return bitstring.pack(self.MASK, self.card_number, self.room)

    @classmethod
    def decode(cls, byte_stream):
        bit_stream = bitstring.BitStream(byte_stream)  # преобразуем в биты
        return cls(
            card_number=bit_stream.read(10).uint,
            room=bit_stream.read(10).uint,
        )


@dataclass
class CardTtlPair(IBinary):
    """
    Класс, представляющий собой пару карточка-ttl
    """
    card_number: int
    time_to_live: int
    MASK: ClassVar[str] = 'uint10, uint10'  # маска для карточки

    def encode(self):
        return bitstring.pack(self.MASK, self.card_number, self.time_to_live)

    @classmethod
    def decode(cls, byte_stream):
        bit_stream = bitstring.BitStream(byte_stream)  # преобразуем в биты
        return cls(
            card_number=bit_stream.read(10).uint,
            time_to_live=bit_stream.read(10).uint,
        )


@dataclass
class Card(IBinary):
    """
    Класс, представляющий собой карточку
    """
    card_number: int
    MASK: ClassVar[str] = 'uint12'  # маска для карточки

    def encode(self):
        return bitstring.pack(self.MASK, self.card_number)

    @classmethod
    def decode(cls, byte_stream):
        bit_stream = bitstring.BitStream(byte_stream)  # преобразуем в биты
        return cls(
            card_number=bit_stream.read(12).uint,
        )
