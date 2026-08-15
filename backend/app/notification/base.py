from abc import ABC, abstractmethod


class NotificationProvider(ABC):
    @abstractmethod
    async def send(self, title: str, body: str) -> None:
        raise NotImplementedError
