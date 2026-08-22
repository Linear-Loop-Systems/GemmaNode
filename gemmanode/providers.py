from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .models import (
    AuthenticationState,
    ConnectionStatus,
    IntegrationStage,
    Resource,
    ResourceType,
)

logger = logging.getLogger(__name__)


@dataclass
class ConnectionTestResult:
    success: bool
    message: str
    status: ConnectionStatus


class ProviderAdapter(Protocol):
    def make_resource(self) -> Resource:
        ...

    def required_secrets(self) -> list[str]:
        ...

    def test_connection(self, resource: Resource, secrets: dict[str, str]) -> ConnectionTestResult:
        ...


@dataclass
class StaticProviderAdapter:
    resource_id: str
    name: str
    provider: str
    resource_type: ResourceType
    stage: IntegrationStage
    capabilities: set[str]
    auth_required: bool = False
    status: ConnectionStatus = ConnectionStatus.NOT_CONFIGURED
    not_implemented_message: str = "Integration is not yet implemented."

    def make_resource(self) -> Resource:
        auth_state = AuthenticationState.NOT_CONFIGURED if self.auth_required else AuthenticationState.NOT_REQUIRED
        return Resource(
            id=self.resource_id,
            name=self.name,
            provider=self.provider,
            type=self.resource_type,
            status=self.status,
            enabled=True,
            capabilities=set(self.capabilities),
            authentication_state=auth_state,
            stage=self.stage,
        )

    def required_secrets(self) -> list[str]:
        return ["api_key"] if self.auth_required else []

    def test_connection(self, resource: Resource, secrets: dict[str, str]) -> ConnectionTestResult:
        return ConnectionTestResult(
            success=False,
            message=self.not_implemented_message,
            status=ConnectionStatus.NOT_IMPLEMENTED,
        )


class LocalProviderAdapter(StaticProviderAdapter):
    def __init__(self) -> None:
        super().__init__(
            resource_id="local-pc",
            name="Local PC",
            provider="local-runtime",
            resource_type=ResourceType.LOCAL_COMPUTE,
            stage=IntegrationStage.AVAILABLE,
            capabilities={"compute", "inference", "local"},
            auth_required=False,
            status=ConnectionStatus.AVAILABLE,
        )

    def test_connection(self, resource: Resource, secrets: dict[str, str]) -> ConnectionTestResult:
        return ConnectionTestResult(True, "Local runtime is available.", ConnectionStatus.AVAILABLE)


class GeminiProviderAdapter(StaticProviderAdapter):
    def __init__(self) -> None:
        super().__init__(
            resource_id="gemini-api",
            name="Gemini",
            provider="gemini",
            resource_type=ResourceType.AI_PROVIDER,
            stage=IntegrationStage.AVAILABLE,
            capabilities={"chat", "reasoning", "generation"},
            auth_required=True,
            status=ConnectionStatus.NOT_CONFIGURED,
        )

    def test_connection(self, resource: Resource, secrets: dict[str, str]) -> ConnectionTestResult:
        api_key = secrets.get("api_key")
        if not api_key:
            return ConnectionTestResult(False, "Gemini API key is missing.", ConnectionStatus.NOT_CONFIGURED)

        request = Request(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}")
        try:
            with urlopen(request, timeout=10) as response:
                if response.status == 200:
                    return ConnectionTestResult(True, "Gemini connection successful.", ConnectionStatus.CONNECTED)
        except HTTPError as exc:
            logger.warning("Gemini connection failed with HTTP status %s", exc.code)
            return ConnectionTestResult(
                False,
                "Gemini connection failed. Check your API key and network connection.",
                ConnectionStatus.FAILED,
            )
        except URLError:
            return ConnectionTestResult(
                False,
                "Gemini connection failed. Check your network connection.",
                ConnectionStatus.FAILED,
            )
        return ConnectionTestResult(False, "Gemini connection failed.", ConnectionStatus.FAILED)


class OpenRouterProviderAdapter(StaticProviderAdapter):
    def __init__(self) -> None:
        super().__init__(
            resource_id="openrouter",
            name="OpenRouter",
            provider="openrouter",
            resource_type=ResourceType.AI_PROVIDER,
            stage=IntegrationStage.AVAILABLE,
            capabilities={"chat", "reasoning", "model-router"},
            auth_required=True,
            status=ConnectionStatus.NOT_CONFIGURED,
        )

    def test_connection(self, resource: Resource, secrets: dict[str, str]) -> ConnectionTestResult:
        api_key = secrets.get("api_key")
        if not api_key:
            return ConnectionTestResult(False, "OpenRouter API key is missing.", ConnectionStatus.NOT_CONFIGURED)

        request = Request("https://openrouter.ai/api/v1/models")
        request.add_header("Authorization", "Bearer " + api_key)
        request.add_header("Accept", "application/json")

        try:
            with urlopen(request, timeout=10) as response:
                if response.status != 200:
                    return ConnectionTestResult(
                        False,
                        "OpenRouter connection failed. Check your API key and network connection.",
                        ConnectionStatus.FAILED,
                    )
                body = json.loads(response.read().decode("utf-8"))
                selected_model = resource.configuration.get("model")
                if selected_model:
                    available_models = {m.get("id") for m in body.get("data", []) if isinstance(m, dict)}
                    if selected_model not in available_models:
                        return ConnectionTestResult(
                            False,
                            "OpenRouter connected but selected model is unavailable for this account.",
                            ConnectionStatus.FAILED,
                        )
                return ConnectionTestResult(True, "OpenRouter connection successful.", ConnectionStatus.CONNECTED)
        except HTTPError:
            return ConnectionTestResult(
                False,
                "OpenRouter connection failed. Check your API key and network connection.",
                ConnectionStatus.FAILED,
            )
        except URLError:
            return ConnectionTestResult(
                False,
                "OpenRouter connection failed. Check your network connection.",
                ConnectionStatus.FAILED,
            )


class PollinationsProviderAdapter(StaticProviderAdapter):
    def __init__(self) -> None:
        super().__init__(
            resource_id="pollinations",
            name="Pollinations AI",
            provider="pollinations",
            resource_type=ResourceType.AI_PROVIDER,
            stage=IntegrationStage.EXPERIMENTAL,
            capabilities={"image-generation", "text-generation"},
            auth_required=False,
            status=ConnectionStatus.UNTESTED,
            not_implemented_message=(
                "Pollinations integration boundary is implemented, but verified credentialed connection testing is not yet implemented."
            ),
        )



def default_adapters() -> dict[str, ProviderAdapter]:
    adapters: dict[str, ProviderAdapter] = {
        "local-pc": LocalProviderAdapter(),
        "gemini-api": GeminiProviderAdapter(),
        "openrouter": OpenRouterProviderAdapter(),
        "pollinations": PollinationsProviderAdapter(),
        "camber": StaticProviderAdapter(
            "camber",
            "Camber",
            "camber",
            ResourceType.CLOUD_COMPUTE,
            IntegrationStage.PLANNED,
            {"cloud-compute"},
            auth_required=True,
            not_implemented_message="Camber integration requires provider-specific API details and is not implemented yet.",
        ),
        "kaggle": StaticProviderAdapter(
            "kaggle",
            "Kaggle",
            "kaggle",
            ResourceType.CLOUD_COMPUTE,
            IntegrationStage.EXPERIMENTAL,
            {"notebook-execution", "cloud-compute"},
            auth_required=True,
            not_implemented_message="Kaggle integration is experimental and connection testing is not implemented yet.",
        ),
        "google-colab": StaticProviderAdapter(
            "google-colab",
            "Google Colab",
            "google-colab",
            ResourceType.CLOUD_COMPUTE,
            IntegrationStage.EXPERIMENTAL,
            {"notebook-execution", "cloud-compute"},
            auth_required=True,
            not_implemented_message="Google Colab integration is experimental and requires OAuth/account flow implementation.",
        ),
        "hugging-face": StaticProviderAdapter(
            "hugging-face",
            "Hugging Face",
            "hugging-face",
            ResourceType.CLOUD_COMPUTE,
            IntegrationStage.REQUIRES_CONFIGURATION,
            {"inference", "model-hosting", "datasets"},
            auth_required=True,
            not_implemented_message="Hugging Face integration boundary exists, but provider-specific connection testing is not implemented yet.",
        ),
        "openhands": StaticProviderAdapter(
            "openhands",
            "OpenHands",
            "openhands",
            ResourceType.AGENT_FRAMEWORK,
            IntegrationStage.EXPERIMENTAL,
            {"agent-execution", "coding"},
            auth_required=False,
            status=ConnectionStatus.UNTESTED,
            not_implemented_message="OpenHands agent abstraction is available, but runtime integration is not implemented yet.",
        ),
        "openclaw": StaticProviderAdapter(
            "openclaw",
            "OpenClaw",
            "openclaw",
            ResourceType.AGENT_FRAMEWORK,
            IntegrationStage.PLANNED,
            {"agent-execution"},
            auth_required=False,
            status=ConnectionStatus.UNTESTED,
            not_implemented_message="OpenClaw integration is planned and not yet implemented.",
        ),
        "hermes": StaticProviderAdapter(
            "hermes",
            "hermes",
            "hermes",
            ResourceType.AGENT_FRAMEWORK,
            IntegrationStage.PLANNED,
            {"agent-execution"},
            auth_required=False,
            status=ConnectionStatus.UNTESTED,
            not_implemented_message="Hermes integration is planned and not yet implemented.",
        ),
        "claude-manual": StaticProviderAdapter(
            "claude-manual",
            "Claude",
            "claude",
            ResourceType.MANUAL_ESCALATION,
            IntegrationStage.AVAILABLE,
            {"manual-escalation", "expert-review"},
            auth_required=False,
            status=ConnectionStatus.AVAILABLE,
            not_implemented_message="Claude manual escalation is represented as a routing target and does not auto-connect.",
        ),
    }
    return adapters
