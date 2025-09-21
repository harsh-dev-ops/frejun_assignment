from abc import ABC, abstractmethod
import uuid


class _TrainHelper(ABC):
    @abstractmethod
    def generate_pnr(self):
        pass
    

class TrainHelper(_TrainHelper):
    def generate_pnr(self):
        return str(uuid.uuid4()).replace('-', '').upper()[:8]
