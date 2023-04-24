from dataclasses import dataclass
from abc import ABC, abstractmethod
import bitstring


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
    card_number: int
    room: int
    MASK: str = 'uint10, uint10'  # маска для пары карточка-комната

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
class Card(IBinary):
    """
    Класс, представляющий собой карточку
    """
    card_number: int
    time_to_live: int | None = None
    MASK: str = 'uint10, uint10'  # базовая маска для карточки. В сумме должно быть 20, т.к. к кода запроса 4

    def encode(self):
        if self.time_to_live is None:
            self.time_to_live = 0  # если нету time_to_live, то ставим его равным нулю, чтоб нормально закодировать
        return bitstring.pack(self.MASK, self.card_number, self.time_to_live)

    @classmethod
    def decode(cls, byte_stream):
        bit_stream = bitstring.BitStream(byte_stream)  # преобразуем в биты
        card_number = bit_stream.read(10).uint  # декодируем номер команты
        instance = cls(
            card_number=card_number,
        )
        time_to_live = bit_stream.read(10).uint  # декодируем TTL
        if time_to_live != 0:
            # если TTL равен нулю, то его не нужно учитывать, а если не равен, то добавляем к инстансу
            instance.time_to_live = time_to_live
        return instance
