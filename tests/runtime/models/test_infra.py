from covalve.runtime.models.infra import (
    BackgroundUnit,
    ConvData,
    GuardRailResponse,
    MCPResponse,
    TextContent,
)
from covalve.runtime.models.metadata import ContentUnit


def test_background_unit_and_conversation_payload():
    background = BackgroundUnit(
        summarize="summary",
        conversation=[
            ConvData(
                user="user",
                assistance="assistant",
                metadata=[
                    ContentUnit(
                        intent="lookup",
                        composition_context="ctx",
                        confidence=0.9,
                    )
                ],
                data={"k": "v"},
            )
        ],
    )

    assert background.summarize == "summary"
    assert background.conversation[0].metadata[0].intent == "lookup"


def test_guardrail_response_and_mcp_response():
    guardrail = GuardRailResponse(reason="out of scope", is_rejected=True)
    response = MCPResponse(
        content=[TextContent(type="text", text="hello")],
        structuredContent={"x": 1},
    )

    assert guardrail.is_rejected is True
    assert response.content[0].text == "hello"
    assert response.structuredContent == {"x": 1}
