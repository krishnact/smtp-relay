import abc
from email.message import EmailMessage

class EmailProvider(abc.ABC):
    @abc.abstractmethod
    def send(self, message: EmailMessage) -> bool:
        pass

    @abc.abstractmethod
    def name(self) -> str:
        pass
