from abc import ABC, abstractmethod

class Encoder(ABC):

    @abstractmethod
    def encode(self, carry, payload):
        pass

    @abstractmethod
    def decode(self, data):
        pass


    