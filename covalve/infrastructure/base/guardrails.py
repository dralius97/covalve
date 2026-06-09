from abc import ABC, abstractmethod
from covalve.runtime.models.infra import BackgroundUnit, GuardRailResponse
from typing import Optional
class GuardrailBase(ABC):
    @abstractmethod
    async def validate(self, query:str, background: Optional[BackgroundUnit] = None) -> GuardRailResponse:...
