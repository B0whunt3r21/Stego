from abc import ABC, abstractmethod

class FileHandler(ABC):
    
    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def save(self):
        pass

