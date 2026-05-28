from infrastructure.base.guardrails import GuardrailBase
from runtime.models.infra import BackgroundUnit, GuardRailResponse

class GuardrailClient(GuardrailBase):
    async def validate(self, query:str, background: BackgroundUnit) -> GuardRailResponse:
        raise NotImplementedError("Log client not implemented yet")