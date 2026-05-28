from abc import ABC, abstractmethod
from runtime.models.infra import BackgroundUnit, GuardRailResponse

class GuardrailBase(ABC):
    @abstractmethod
    async def validate(self, query:str, background: BackgroundUnit) -> GuardRailResponse:...
