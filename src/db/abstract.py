from abc import ABC, abstractmethod


class AsyncCacheStorage(ABC):
    @abstractmethod
    async def get(self, key: str, **kwargs):
        pass

    @abstractmethod
    async def set(self, key: str, value: str, expire: int, **kwargs):
        pass
    
    
class AsyncSearchEngine(ABC):
    @abstractmethod
    async def search(self,  **kwargs):
        pass
